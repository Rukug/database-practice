import csv
from pathlib import Path

from flask import Flask, render_template

app = Flask(__name__)

STUDENTS_CSV = Path(__file__).parent / "database" / "students.csv"


def load_student_names():
    names = []
    with STUDENTS_CSV.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            names.append(row["full_name"])
    return names


@app.route("/")
def index():
    names = load_student_names()
    return render_template("index.html", names=names)


if __name__ == "__main__":
    app.run(debug=True)
