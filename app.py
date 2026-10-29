import os
from pathlib import Path

import psycopg2
from flask import Flask, jsonify, render_template

app = Flask(__name__)


def database_url():
    url = os.environ.get("DATABASE_URL")
    if not url:
        for line in (Path(__file__).parent / "database" / ".env").read_text().splitlines():
            if line.startswith("DATABASE_URL="):
                url = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    if "sslmode=" not in url:
        url += ("&" if "?" in url else "?") + "sslmode=require"
    return url


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/names")
def names():
    with psycopg2.connect(database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT full_name FROM students ORDER BY full_name")
            return jsonify([row[0] for row in cur.fetchall()])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
