import csv
import os
from pathlib import Path

from flask import Flask, render_template

app = Flask(__name__)

STUDENTS_CSV = Path(__file__).parent / "database" / "students.csv"

SKILL_COLUMNS = [
    ("skill_programming", "Programming"),
    ("skill_data_stats", "Data & stats"),
    ("skill_frontend_design", "Frontend design"),
    ("skill_business_pitch", "Business pitch"),
]


def parse_rating(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def load_page_data():
    names = []
    totals = {column: 0.0 for column, _ in SKILL_COLUMNS}
    counts = {column: 0 for column, _ in SKILL_COLUMNS}

    with STUDENTS_CSV.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            names.append(row["full_name"])
            for column, _ in SKILL_COLUMNS:
                rating = parse_rating(row.get(column))
                if rating is not None:
                    totals[column] += rating
                    counts[column] += 1

    skill_averages = []
    for column, label in SKILL_COLUMNS:
        if counts[column] == 0:
            average = "No ratings"
        else:
            average = f"{totals[column] / counts[column]:.2f}"
        skill_averages.append({"label": label, "average": average})

    return names, skill_averages


@app.route("/")
def index():
    names, skill_averages = load_page_data()
    return render_template("index.html", names=names, skill_averages=skill_averages)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
