"""Load and prepare applicant data for the PostgreSQL database."""

import json
import os
import re
from datetime import datetime

import psycopg
from psycopg import sql
from psycopg import Error


DATA_FILE = "llm_extend_applicant_data.json"


def get_connection():
    """Create and return a PostgreSQL database connection."""
    return psycopg.connect(
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
    )


def extract_p_id(url):
    """Extract the applicant ID from a GradCafe result URL."""
    if not url:
        return None

    match = re.search(r"/result/(\d+)", url)

    if match:
        return int(match.group(1))

    return None


def clean_float(value, prefix=None):
    """Convert an applicant data value to a cleaned float."""
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
    """Convert an applicant date string to a date object."""
    if not value:
        return None

    try:
        return datetime.strptime(value, "%b %d, %Y").date()
    except ValueError:
        return None


def create_table(cursor):
    """Create the applicants table if it does not already exist."""
    stmt = sql.SQL(
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
        )
        """
    )

    cursor.execute(stmt)


def load_data():
    """Load applicant data from JSON into the PostgreSQL database."""
    connection = None

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            applicants = json.load(file)

        connection = get_connection()

        with connection.cursor() as cursor:  # pylint: disable=no-member
            create_table(cursor)

            inserted_count = 0

            for applicant in applicants:
                p_id = extract_p_id(applicant.get("url"))

                if p_id is None:
                    continue

                values = (
                    p_id,
                    f"{applicant.get('program', '')}, "
                    f"{applicant.get('university', '')}",
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

                stmt = sql.SQL(
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
                    """
                )

                cursor.execute(stmt, values)

                if cursor.rowcount == 1:
                    inserted_count += 1

        connection.commit()  # pylint: disable=no-member

        print(f"Successfully processed {len(applicants)} records.")
        print(f"New records inserted: {inserted_count}")

    except Exception as error:
        if connection:
            connection.rollback()

        print(f"Error loading data: {error}")

    finally:
        if connection:
            connection.close()  # pylint: disable=no-member


if __name__ == "__main__":  # pragma: no cover
    load_data()
