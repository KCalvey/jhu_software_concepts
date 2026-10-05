"""Run PostgreSQL queries used by the applicant analysis application."""

# pylint: disable=duplicate-code

import os

import psycopg
from psycopg import sql

MAX_LIMIT = 100


def safe_limit(value):
    """Clamp a requested query limit between 1 and MAX_LIMIT."""
    return max(1, min(int(value), MAX_LIMIT))

def get_connection():
    """Create and return a PostgreSQL database connection."""
    return psycopg.connect(
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
    )

def question_1(cursor):
    """Print the number of Fall 2026 applicants."""
    statement = sql.SQL(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE LOWER(term) = %s
        LIMIT 1;
        """
    )

    params = ("fall 2026",)

    cursor.execute(statement, params)

    count = cursor.fetchone()[0]

    print(f"Fall 2026 applicant count: {count}")

def question_2(cursor):
    """Print the percentage of international applicants."""
    statement = sql.SQL(
        """
        SELECT
            100.0 *
            COUNT(*) FILTER (
                WHERE LOWER(TRIM(us_or_international)) = %s
            )
            /
            NULLIF(COUNT(*), 0)
        FROM applicants
        WHERE us_or_international IS NOT NULL
          AND TRIM(us_or_international) <> %s
        LIMIT 1;
        """
    )

    params = ("international", "")

    cursor.execute(statement, params)

    result = cursor.fetchone()

    if result is None:
        print("Percent international: no result returned")
        return

    percent_international = result[0]

    print(f"Percent international: {percent_international:.2f}%")

def question_3(cursor):
    """Print average GPA and GRE scores for applicants."""
    statement = sql.SQL(
        """
        SELECT
            AVG(gpa),
            AVG(gre),
            AVG(gre_v),
            AVG(gre_aw)
        FROM applicants
        LIMIT 1;
        """
    )

    cursor.execute(statement)

    result = cursor.fetchone()

    if result is None:
        print("Question 3: no result returned")
        return

    avg_gpa, avg_gre, avg_gre_v, avg_gre_aw = result

    print(f"Average GPA: {avg_gpa:.2f}")
    print(f"Average GRE Quantitative: {avg_gre:.2f}")
    print(f"Average GRE Verbal: {avg_gre_v:.2f}")
    print(f"Average GRE Analytical Writing: {avg_gre_aw:.2f}")

def question_4(cursor):
    """Print the average GPA for American Fall 2026 applicants."""
    statement = sql.SQL(
        """
        SELECT AVG(gpa)
        FROM applicants
        WHERE LOWER(term) = %s
          AND LOWER(TRIM(us_or_international)) = %s
          AND gpa IS NOT NULL
        LIMIT 1;
        """
    )

    params = ("fall 2026", "american")

    cursor.execute(statement, params)

    avg_gpa = cursor.fetchone()[0]

    print(f"Average GPA American Fall 2026: {avg_gpa:.2f}")

def question_5(cursor):
    """Print the Fall 2025 acceptance percentage."""
    statement = sql.SQL(
        """
        SELECT
            100.0 *
            SUM(
                CASE
                    WHEN LOWER(status) LIKE %s
                    THEN 1
                    ELSE 0
                END
            )
            /
            NULLIF(COUNT(*), 0)
        FROM applicants
        WHERE LOWER(term) = %s
        LIMIT 1;
        """
    )

    params = ("%accept%", "fall 2025")

    cursor.execute(statement, params)

    acceptance_percent = cursor.fetchone()[0]

    print(f"Fall 2025 acceptance percentage: {acceptance_percent:.2f}%")

def question_6(cursor):
    """Print the average GPA of accepted Fall 2026 applicants."""
    statement = sql.SQL(
        """
        SELECT AVG(gpa)
        FROM applicants
        WHERE LOWER(term) = %s
          AND LOWER(status) LIKE %s
          AND gpa IS NOT NULL
        LIMIT 1;
        """
    )

    params = ("fall 2026", "%accept%")

    cursor.execute(statement, params)

    avg_gpa = cursor.fetchone()[0]

    print(f"Average GPA accepted Fall 2026: {avg_gpa:.2f}")

def question_7(cursor):
    """Print the count of Johns Hopkins computer science master's applicants."""
    statement = sql.SQL(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE LOWER(program) LIKE %s
          AND (
              LOWER(program) LIKE %s
              OR LOWER(program) LIKE %s
          )
          AND LOWER(degree) LIKE %s
        LIMIT 1;
        """
    )

    params = (
        "%computer science%",
        "%johns hopkins university%",
        "%jhu%",
        "%master%",
    )

    cursor.execute(statement, params)

    count = cursor.fetchone()[0]

    print(f"JHU Computer Science master's count: {count}")

def question_8(cursor):
    """Return the count of qualifying applicants using original fields."""
    statement = sql.SQL(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE LOWER(term) = %s
          AND LOWER(status) LIKE %s
          AND LOWER(degree) = %s
          AND LOWER(program) LIKE %s
          AND (
              LOWER(program) LIKE %s
              OR LOWER(program) LIKE %s
              OR LOWER(program) LIKE %s
              OR LOWER(program) LIKE %s
              OR LOWER(program) LIKE %s
          )
        LIMIT 1;
        """
    )

    params = (
        "fall 2026",
        "%accept%",
        "phd",
        "%computer science%",
        "%georgetown university%",
        "%massachusetts institute of technology%",
        "%mit%",
        "%stanford university%",
        "%carnegie mellon university%",
    )

    cursor.execute(statement, params)

    count = cursor.fetchone()[0]

    return count

def question_9(cursor, original_count):
    """Compare LLM-generated applicant fields with original-field results."""
    statement = sql.SQL(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE LOWER(term) = %s
          AND LOWER(status) LIKE %s
          AND LOWER(degree) = %s
          AND LOWER(llm_generated_program) LIKE %s
          AND (
              LOWER(llm_generated_university) LIKE %s
              OR LOWER(llm_generated_university) LIKE %s
              OR LOWER(llm_generated_university) LIKE %s
              OR LOWER(llm_generated_university) LIKE %s
              OR LOWER(llm_generated_university) LIKE %s
          )
        LIMIT 1;
        """
    )

    params = (
        "fall 2026",
        "%accept%",
        "phd",
        "%computer science%",
        "%georgetown university%",
        "%massachusetts institute of technology%",
        "%mit%",
        "%stanford university%",
        "%carnegie mellon university%",
    )

    cursor.execute(statement, params)

    llm_count = cursor.fetchone()[0]
    difference = llm_count - original_count

    print(f"Original-field count: {original_count}")
    print(f"LLM-field count: {llm_count}")
    print(f"Difference: {difference:+d}")

def question_10(cursor):
    """Print the top universities by application count."""
    statement = sql.SQL(
        """
        SELECT llm_generated_university, COUNT(*) AS application_count
        FROM applicants
        WHERE llm_generated_university IS NOT NULL
          AND TRIM(llm_generated_university) <> %s
        GROUP BY llm_generated_university
        ORDER BY application_count DESC
        LIMIT %s;
        """
    )

    limit = safe_limit(5)
    params = ("", limit)

    cursor.execute(statement, params)

    results = cursor.fetchall()

    print("Top 5 universities by application count:")
    for university, count in results:
        print(f"{university}: {count}")

def question_11(cursor):
    """Print the average GPA of Johns Hopkins applicants."""
    statement = sql.SQL(
        """
        SELECT AVG(gpa)
        FROM applicants
        WHERE LOWER(llm_generated_university) LIKE %s
          AND gpa IS NOT NULL
        LIMIT 1;
        """
    )

    params = ("%johns hopkins%",)

    cursor.execute(statement, params)

    avg_gpa = cursor.fetchone()[0]

    print(
        f"Average GPA of Johns Hopkins University applicants: "
        f"{avg_gpa:.2f}"
    )

def get_applicant_summary(cursor):
    """Return a summary of one applicant record."""
    statement = sql.SQL(
        """
        SELECT
            p_id,
            program,
            status,
            term,
            gpa
        FROM applicants
        LIMIT %s;
        """
    )

    limit = safe_limit(1)
    params = (limit,)

    cursor.execute(statement, params)

    row = cursor.fetchone()

    if row is None:
        return {}

    return {
        "p_id": row[0],
        "program": row[1],
        "status": row[2],
        "term": row[3],
        "gpa": row[4],
    }

def main():
    """Run all applicant database queries."""
    connection = None

    try:
        connection = get_connection()

        with connection.cursor() as cursor:  # pylint: disable=no-member
            question_1(cursor)
            question_2(cursor)
            question_3(cursor)
            question_4(cursor)
            question_5(cursor)
            question_6(cursor)
            question_7(cursor)

            original_count = question_8(cursor)
            question_9(cursor, original_count)

            question_10(cursor)
            question_11(cursor)

    except Exception as error:
        print(f"Error running queries: {error}")

    finally:
        if connection:
            connection.close()  # pylint: disable=no-member


if __name__ == "__main__":  # pragma: no cover
    main()
