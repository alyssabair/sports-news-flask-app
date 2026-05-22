from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return send_from_directory(os.path.dirname(__file__), "index.html")

@app.route("/news")
def news():
    # Dummy data for now
    articles = [
        {"title": "NBA: Lakers Win Thriller", "sport": "NBA", "summary": "Lakers beat Celtics 110-108", "date": "2025-12-09"},
        {"title": "NFL: Patriots Dominate", "sport": "NFL", "summary": "Patriots defeat Jets 24-10", "date": "2025-12-09"},
        {"title": "PGA: Big Win in Orlando", "sport": "PGA", "summary": "Top player claims victory at Orlando Open", "date": "2025-12-09"}
    ]
    return jsonify(articles)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
