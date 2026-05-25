from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)

# === SERVE YOUR FRONTEND ===
@app.route("/")
def index():
    return send_from_directory(os.path.dirname(__file__), "index.html")

# === REAL NBA DATA ROUTE ===
@app.route("/api/nba")
def nba_data_route():
    url = "https://site.api.espn.com/apis/v2/sports/basketball/nba/standings?season=2025"
    try:
        r = requests.get(url).json()
        teams_list = []

        for conf in r.get("children", []):
            for entry in conf["standings"]["entries"]:
                team_name = entry["team"]["displayName"]
                stats = entry["stats"]
                # Try to get win percentage since avg points is inactive during playoffs
                win_pct = next((s["displayValue"] for s in stats if s["name"]=="winPercent"), "0.00")
                teams_list.append({"team": team_name, "stat": win_pct})

        # Fallback if API fails
        if not teams_list:
            teams_list = [{"team": "Celtics", "stat": ".793"}, {"team": "Thunder", "stat": ".695"}]

        # Return the top 5
        return jsonify(sorted(teams_list, key=lambda x: float(x["stat"]), reverse=True)[:5])
    except Exception as e:
        print("Error fetching NBA:", e)
        return jsonify([{"team": "Error loading live standings", "stat": ""}])

# === REAL PGA DATA ROUTE ===
@app.route("/api/pga")
def pga_data_route():
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/golf/pga/scoreboard"
        r = requests.get(url).json()

        if not r.get("events"):
            return jsonify([{"player": "No active live tournament", "score": "N/A"}])

        competitors = r["events"][0]["competitions"][0]["competitors"][:5]
        pga_list = []
        for c in competitors:
            name = c["athlete"]["displayName"]
            score = c.get("score", "E")
            pga_list.append({"player": name, "score": score})
        return jsonify(pga_list)
    except Exception as e:
        print("Error fetching PGA:", e)
        return jsonify([{"player": "Error loading leaderboard", "score": ""}])

# === YOUR CLEAN LOCAL NEWS ROUTE ===
@app.route("/news")
def news():
    articles = [
        {"title": "PGA Championship Action Underway", "sport": "PGA"},
        {"title": "NBA Playoffs: Conference Finals Intensity Ramps Up", "sport": "NBA"},
        {"title": "NFL Schedule Release Highlights Key Matchups", "sport": "NFL"}
    ]
    return jsonify(articles)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)