
from flask import Flask, render_template, request
import trafilatura
import requests
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
API_KEY = os.getenv("API_KEY")

@app.route("/")
def index():
    return render_template("index.html", message="")

@app.route("/submit", methods=["POST"])
def submit():
    url = request.form.get("url", "").strip()

    if not url:
        return render_template("index.html", message="Please enter a URL.")

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        article = trafilatura.fetch_url(url)
        text = trafilatura.extract(article) if article else None

        if not text:
            return render_template("index.html", message="No article found.")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/free",
                "messages": [
                    {
                        "role": "user",
                        "content": f"""Summarize this article in 5-15 sentences. Make it clear and don't use characters such as #, ;, or :. Don't add titles or headings, only paragraphs. No need to do PLOT: that is just weird.
                        {text}"""
                    }
                ]
            },
            timeout=60
        )

        print("Status:", response.status_code)
        print("Response:", response.text)

        response.raise_for_status()

        summary = response.json()["choices"][0]["message"]["content"]

        return render_template("index.html", message=summary)

    except Exception as e:
        print("ERROR:", e)
        return render_template("index.html", message=str(e))

if __name__ == "__main__":
    app.run(debug=True)
