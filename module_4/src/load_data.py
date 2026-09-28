import json
import os
import re
from datetime import datetime

import psycopg


DATA_FILE = "llm_extend_applicant_data.json"


def get_connection():
    return psycopg.connect(
        dbname=os.getenv("DB_NAME", "module3_db"),
        user=os.getenv("DB_USER", "karicalvey"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )


def extract_p_id(url):
    if not url:
        return None

    match = re.search(r"/result/(\d+)", url)

    if match:
        return int(match.group(1))

    return None


def clean_float(value, prefix=None):
    if value is None:
        return None

    text = str(value).strip()

    if prefix:
        text = text.replace(prefix, "").strip()

    try:
        return float(text)
    except ValueError:
        return None


def clean_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(value, "%b %d, %Y").date()
    except ValueError:
        return None


def create_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS applicants (
            p_id INTEGER PRIMARY KEY,
            program TEXT,
            comments TEXT,
            date_added DATE,
            url TEXT,
            status TEXT,
            term TEXT,
            us_or_international TEXT,
            gpa FLOAT,
            gre FLOAT,
            gre_v FLOAT,
            gre_aw FLOAT,
            degree TEXT,
            llm_generated_program TEXT,
            llm_generated_university TEXT
        );
        """
    )


def load_data():
    connection = None

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            applicants = json.load(file)

        connection = get_connection()

        with connection.cursor() as cursor:
            create_table(cursor)

            inserted_count = 0

            for applicant in applicants:
                p_id = extract_p_id(applicant.get("url"))

                if p_id is None:
                    continue

                values = (
                    p_id,
                    f"{applicant.get('program', '')}, {applicant.get('university', '')}".strip(", "),
                    applicant.get("comments"),
                    clean_date(applicant.get("date_added")),
                    applicant.get("url"),
                    applicant.get("status"),
                    applicant.get("term"),
                    applicant.get("student_type"),
                    clean_float(applicant.get("gpa"), "GPA"),
                    clean_float(applicant.get("gre"), "GRE"),
                    clean_float(applicant.get("gre_v"), "GRE V"),
                    clean_float(applicant.get("gre_aw"), "GRE AW"),
                    applicant.get("degree"),
                    applicant.get("standardized_program"),
                    applicant.get("standardized_university"),
                )

                cursor.execute(
                    """
                    INSERT INTO applicants (
                        p_id,
                        program,
                        comments,
                        date_added,
                        url,
                        status,
                        term,
                        us_or_international,
                        gpa,
                        gre,
                        gre_v,
                        gre_aw,
                        degree,
                        llm_generated_program,
                        llm_generated_university
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (p_id) DO NOTHING;
                    """,
                    values,
                )

                if cursor.rowcount == 1:
                    inserted_count += 1

        connection.commit()

        print(f"Successfully processed {len(applicants)} records.")
        print(f"New records inserted: {inserted_count}")

    except Exception as error:
        if connection:
            connection.rollback()

        print(f"Error loading data: {error}")

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":  # pragma: no cover
    load_data()