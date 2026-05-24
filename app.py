import matplotlib
matplotlib.use('Agg')  # Required so matplotlib can save images without a GUI on Render
import matplotlib.pyplot as plt
from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
import io
import os
import requests

app = Flask(__name__)
CORS(app)

# === YOUR ORIGINAL HOME ROUTE ===
@app.route("/")
def index():
    return send_from_directory(os.path.dirname(__file__), "index.html")

# === YOUR ORIGINAL NEWS ROUTE ===
@app.route("/news")
def news():
    articles = [
        {"title": "NBA: Lakers Win Thriller", "sport": "NBA", "summary": "Lakers beat Celtics 110-108", "date": "2025-12-09"},
        {"title": "NFL: Patriots Dominate", "sport": "NFL", "summary": "Patriots defeat Jets 24-10", "date": "2025-12-09"},
        {"title": "PGA: Big Win in Orlando", "sport": "PGA", "summary": "Top player claims victory at Orlando Open", "date": "2025-12-09"}
    ]
    return jsonify(articles)

# === YOUR EXACT ORIGINAL NBA DATA FUNCTION ===
def get_nba_data():
    """Fetch NBA standings and return top 5 teams by avg points"""
    url = "https://site.api.espn.com/apis/v2/sports/basketball/nba/standings?season=2025"
    try:
        r = requests.get(url).json()
        teams, avg_points = [], []

        for conf in r.get("children", []):
            for entry in conf["standings"]["entries"]:
                team_name = entry["team"]["displayName"]
                stats = entry["stats"]
                avg_pts = next((float(s["displayValue"]) for s in stats if s["name"]=="avgPointsPerGame"), 0)
                teams.append(team_name)
                avg_points.append(avg_pts)

        if not teams:
            # fallback data
            teams = ["Team A", "Team B", "Team C", "Team D", "Team E"]
            avg_points = [112.5, 110.3, 109.8, 107.5, 106.2]

        # top 5 teams
        top_teams = sorted(zip(teams, avg_points), key=lambda x: x[1], reverse=True)[:5]
        team_names, team_avg_pts = zip(*top_teams)
        return team_names, team_avg_pts

    except Exception as e:
        print("Error fetching NBA data:", e)
        # fallback example data
        team_names = ["Team A", "Team B", "Team C", "Team D", "Team E"]
        team_avg_pts = [112.5, 110.3, 109.8, 107.5, 106.2]
        return team_names, team_avg_pts

# === YOUR EXACT ORIGINAL NBA CHART ROUTE ===
@app.route("/nba-chart.png")
def nba_chart():
    team_names, team_avg_pts = get_nba_data()

    plt.figure(figsize=(8,5))
    plt.plot(team_names, team_avg_pts, marker='o', color='blue', linewidth=2)
    plt.title("Top 5 NBA Teams by Avg Points per Game")
    plt.ylabel("Avg Points")
    plt.xlabel("Team")
    plt.ylim(0, max(team_avg_pts)+10)
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)