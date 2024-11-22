import sqlite3
import pandas as pd
from flask import Flask, render_template
from datetime import datetime

# Configuration
BASE_DIRECTORY = r"C:\Users\howar\football_research_advanced\2.0\England\Football_Predictions\data"
DATABASE_PATH = f"{BASE_DIRECTORY}\\football_data.db"

# Initialize Flask app
app = Flask(
    __name__,
    template_folder=r"C:\Users\howar\football_research_advanced\2.0\England\Football_Predictions\templates"
)

@app.route("/")
def home():
    """
    Fetch predictions with odds and team logos from the database, process them, and render the HTML page.
    """
    # Connect to the database
    conn = sqlite3.connect(DATABASE_PATH)

    # Query to fetch predictions and team logos
    query = """
    SELECT 
        p.fixture_id,
        p.date,
        p.home_team_name,
        tv_home.team_logo AS home_team_logo,
        p.away_team_name,
        tv_away.team_logo AS away_team_logo,
        p.predicted_result,
        p.home_probability,
        p.draw_probability,
        p.away_probability,
        p.best_home_odd,
        p.best_draw_odd,
        p.best_away_odd
    FROM predictions p
    LEFT JOIN team_visuals tv_home ON p.home_team_name = tv_home.team_name
    LEFT JOIN team_visuals tv_away ON p.away_team_name = tv_away.team_name
    """
    predictions = pd.read_sql_query(query, conn)
    conn.close()

    # Convert probabilities to percentages
    predictions['home_probability'] = (predictions['home_probability']).round(2)
    predictions['draw_probability'] = (predictions['draw_probability']).round(2)
    predictions['away_probability'] = (predictions['away_probability']).round(2)

    # Format the date column
    def format_date(date_str):
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")  # Parse the original date format
        suffix = (
            "th" if 11 <= dt.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(dt.day % 10, "th")
        )
        formatted_date = dt.strftime(f"%d{suffix} %B %y - %H:%M")
        return formatted_date

    predictions['date'] = predictions['date'].apply(format_date)

    # **Sort the predictions by home win probability**
    predictions = predictions.sort_values(by='home_probability', ascending=False)

    # Render the predictions table to HTML
    return render_template(
        "predictions.html",
        predictions=predictions.to_dict(orient="records"),
        current_year=datetime.now().year
    )


if __name__ == "__main__":
    app.run(debug=True)
