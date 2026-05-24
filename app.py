import matplotlib
matplotlib.use('Agg')  # Required for Render Linux servers
import matplotlib.pyplot as plt
from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
import io
import os
import requests

app = Flask(__name__)
CORS(app)

# === SERVE YOUR FRONTEND ===
@app.route("/")
def index():
    return send_from_directory(os.path.dirname(__file__), "index.html")

# === YOUR ORIGINAL NBA DATA SCRAPER ===
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
                
                # Your exact loop looking for avgPointsPerGame
                avg_pts = next((float(s["displayValue"]) for s in stats if s["name"]=="avgPointsPerGame"), 0)
                teams.append(team_name)
                avg_points.append(avg_pts)

        if not teams or all(v == 0 for v in avg_points):
            # Fallback data if API yields empty array or all zeros during playoffs
            teams = ["Team A", "Team B", "Team C", "Team D", "Team E"]
            avg_points = [112.5, 110.3, 109.8, 107.5, 106.2]

        top_teams = sorted(zip(teams, avg_points), key=lambda x: x[1], reverse=True)[:5]
        team_names, team_avg_pts = zip(*top_teams)
        return team_names, team_avg_pts

    except Exception as e:
        print("Error fetching NBA data:", e)
        team_names = ["Team A", "Team B", "Team C", "Team D", "Team E"]
        team_avg_pts = [112.5, 110.3, 109.8, 107.5, 106.2]
        return team_names, team_avg_pts

# === YOUR ORIGINAL NBA CHART GENERATOR ===
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

# === YOUR ORIGINAL PGA DATA SCRAPER ===
def get_pga_data():
    """Fetch live PGA scoreboard data from ESPN API."""
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/golf/pga/scoreboard"
        r = requests.get(url).json()

        if not r.get("events"):
            # Fallback if no live tournament is actively running
            players = ["Scottie Scheffler", "Rory McIlroy", "Jon Rahm", "Patrick Cantlay", "Viktor Hovland"]
            scores = [10, 9, 8, 7, 6]
            return players, scores

        competitors = r["events"][0]["competitions"][0]["competitors"][:5]
        players = [c["athlete"]["displayName"] for c in competitors]

        scores = []
        for c in competitors:
            try:
                scores.append(int(c.get("score", 0)))
            except:
                scores.append(0)

        return players, scores
    except Exception as e:
        print("Error fetching data:", e)
        players = ["Scottie Scheffler", "Rory McIlroy", "Jon Rahm", "Patrick Cantlay", "Viktor Hovland"]
        scores = [10, 9, 8, 7, 6]
        return players, scores

# === YOUR ORIGINAL PGA CHART GENERATOR ===
@app.route("/pga-chart.png")
def pga_chart_route():
    players, scores = get_pga_data()
    
    plt.figure(figsize=(6,4))
    plt.bar(players, scores, color='skyblue')
    plt.title("Top 5 PGA Players - Live Tournament")
    plt.ylabel("Score")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)