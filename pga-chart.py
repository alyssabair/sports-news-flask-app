# pga_chart.py
from flask import Flask, send_file
import matplotlib.pyplot as plt
import io
import requests
import sys

app = Flask(__name__)

# Sample or live PGA data function
def get_pga_data():
    """
    Fetch live PGA scoreboard data from ESPN API.
    Returns two lists: player names and scores (as integers)
    """
    try:
        url = "https://site.api.espn.com/apis/site/v2/sports/golf/pga/scoreboard"
        r = requests.get(url).json()

        if not r.get("events"):
            return [], []

        competitors = r["events"][0]["competitions"][0]["competitors"][:5]
        players = [c["athlete"]["displayName"] for c in competitors]

        # Convert scores to integers; replace missing/'E' with 0
        scores = []
        for c in competitors:
            try:
                scores.append(int(c.get("score", 0)))
            except:
                scores.append(0)

        return players, scores
    except Exception as e:
        print("Error fetching data:", e)
        return [], []

# Function to generate a Matplotlib chart and return buffer
def create_chart(players, scores):
    plt.figure(figsize=(6,4))
    plt.bar(players, scores, color='skyblue')
    plt.title("Top 5 PGA Players - Live Tournament")
    plt.ylabel("Score")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

# Flask route to serve chart
@app.route("/pga-chart.png")
def pga_chart_route():
    players, scores = get_pga_data()
    buf = create_chart(players, scores)
    return send_file(buf, mimetype='image/png')

# Optional: run locally to see chart
def show_chart_locally():
    players, scores = get_pga_data()
    if not players:
        # If no live data, use example data
        players = ["Scottie Scheffler", "Rory McIlroy", "Jon Rahm", "Patrick Cantlay", "Viktor Hovland"]
        scores = [10, 9, 8, 7, 6]

    plt.figure(figsize=(6,4))
    plt.bar(players, scores, color='skyblue')
    plt.title("Top 5 PGA Players - Live Tournament")
    plt.ylabel("Score")
    plt.tight_layout()
    plt.show()

# Main entry
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        # Run locally to view chart
        show_chart_locally()
    else:
        # Run Flask server
        app.run(debug=True)
