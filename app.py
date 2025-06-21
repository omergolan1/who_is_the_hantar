from flask import Flask, request, redirect, render_template, send_file, make_response
from wordcloud import WordCloud
import os
import json
from collections import Counter, defaultdict

app = Flask(__name__)
submitted_words = []

ip_submissions = defaultdict(list)  # Maps IP -> list of submitted words
HANTAR_NAME = "vica"
MAX_SUB = 5


@app.route("/", methods=["GET", "POST"])
def index():
    global submitted_words, ip_submissions

    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    print(user_ip)
    user_words = ip_submissions[user_ip]

    if request.method == "POST":
        if len(user_words) >= MAX_SUB:
            return redirect("/")  # Submission limit reached

        word = request.form.get("word")
        if word:
            word = word.strip().lower()
            submitted_words.append(word)
            user_words.append(word)
            ip_submissions[user_ip] = user_words

        return redirect("/")

    return render_template("index.html", submitted=len(user_words), max_submissions=MAX_SUB)


@app.route("/wordcloud.png")
def wordcloud_image():
    global submitted_words

    # Count occurrences
    counts = Counter(submitted_words)

    # Scale frequencies: each word gets size = count * 5
    scaled_freq = {word: (count * 10 if word == HANTAR_NAME else count) for word, count in counts.items()}
    print(counts.keys())
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        min_font_size=5,
        max_font_size=300,
        relative_scaling=1  # force exact frequency-based sizing
    ).generate_from_frequencies(scaled_freq)

    wordcloud.to_file("static/wordcloud.png")
    return send_file("static/wordcloud.png", mimetype='image/png')

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run()
