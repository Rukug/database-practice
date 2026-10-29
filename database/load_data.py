"""Create schema.sql tables on Railway and load the local CSVs."""

import csv
import os
from pathlib import Path

import psycopg2

BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR / ".env"


def read_database_url():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "DATABASE_URL":
            return value.strip().strip('"').strip("'")
    raise SystemExit(f"DATABASE_URL not found in {ENV_PATH}")


def empty_to_none(value):
    if value is None:
        return None
    text = value.strip()
    return text if text else None


def load_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def reset_serial(cursor, table, column):
    cursor.execute(
        """
        SELECT setval(
            pg_get_serial_sequence(%s, %s),
            COALESCE((SELECT MAX({column}) FROM {table}), 1)
        )
        """.format(column=column, table=table),
        (table, column),
    )


def main():
    url = read_database_url()
    if "sslmode=" not in url:
        url = url + ("&" if "?" in url else "?") + "sslmode=require"

    students = load_csv(BASE_DIR / "students.csv")
    tools = load_csv(BASE_DIR / "tools.csv")
    slots = load_csv(BASE_DIR / "availability_slots.csv")
    student_tools = load_csv(BASE_DIR / "student_tools.csv")
    student_availability = load_csv(BASE_DIR / "student_availability.csv")
    schema_sql = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")

    connection = psycopg2.connect(url)
    connection.autocommit = False
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DROP TABLE IF EXISTS student_availability, student_tools,
                    availability_slots, tools, students CASCADE
                """
            )
            cursor.execute(schema_sql)

            cursor.executemany(
                """
                INSERT INTO students (
                    student_id, netid, full_name, school_year, intro_programming,
                    skill_programming, skill_data_stats, skill_frontend_design,
                    skill_business_pitch, working_style, interests, semester_goal,
                    submitted_at
                ) VALUES (
                    %(student_id)s, %(netid)s, %(full_name)s, %(school_year)s,
                    %(intro_programming)s, %(skill_programming)s, %(skill_data_stats)s,
                    %(skill_frontend_design)s, %(skill_business_pitch)s,
                    %(working_style)s, %(interests)s, %(semester_goal)s,
                    %(submitted_at)s
                )
                """,
                [
                    {
                        **row,
                        "working_style": empty_to_none(row.get("working_style")),
                        "interests": empty_to_none(row.get("interests")),
                        "semester_goal": empty_to_none(row.get("semester_goal")),
                    }
                    for row in students
                ],
            )
            cursor.executemany(
                "INSERT INTO tools (tool_id, tool_name) VALUES (%(tool_id)s, %(tool_name)s)",
                tools,
            )
            cursor.executemany(
                """
                INSERT INTO availability_slots (slot_id, slot_name)
                VALUES (%(slot_id)s, %(slot_name)s)
                """,
                slots,
            )
            cursor.executemany(
                """
                INSERT INTO student_tools (student_id, tool_id)
                VALUES (%(student_id)s, %(tool_id)s)
                """,
                student_tools,
            )
            cursor.executemany(
                """
                INSERT INTO student_availability (student_id, slot_id)
                VALUES (%(student_id)s, %(slot_id)s)
                """,
                student_availability,
            )

            reset_serial(cursor, "students", "student_id")
            reset_serial(cursor, "tools", "tool_id")
            reset_serial(cursor, "availability_slots", "slot_id")

            cursor.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM students),
                    (SELECT COUNT(*) FROM tools),
                    (SELECT COUNT(*) FROM availability_slots),
                    (SELECT COUNT(*) FROM student_tools),
                    (SELECT COUNT(*) FROM student_availability)
                """
            )
            counts = cursor.fetchone()
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    labels = (
        "students",
        "tools",
        "availability_slots",
        "student_tools",
        "student_availability",
    )
    print("Loaded schema.sql and CSV rows into Railway:")
    for label, count in zip(labels, counts):
        print(f"  {label}: {count}")


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    main()
