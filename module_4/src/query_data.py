import os

import psycopg

import psycopg

def get_connection():
    return psycopg.connect(
        dbname=os.getenv("DB_NAME", "module3_db"),
        user=os.getenv("DB_USER", "karicalvey"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )
def question_1(cursor):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE LOWER(term) = 'fall 2026';
        """
    )

    count = cursor.fetchone()[0]

    print(f"Fall 2026 applicant count: {count}")

def question_2(cursor):
    cursor.execute(
        """
        SELECT
            100.0 *
            COUNT(*) FILTER (
                WHERE LOWER(TRIM(us_or_international)) = 'international'
            )
            /
            NULLIF(COUNT(*), 0)
        FROM applicants
        WHERE us_or_international IS NOT NULL
          AND TRIM(us_or_international) <> '';
        """
    )

    result = cursor.fetchone()

    if result is None:
        print("Percent international: no result returned")
        return

    percent_international = result[0]

    print(f"Percent international: {percent_international:.2f}%")

def question_3(cursor):
    cursor.execute(
        """
        SELECT
            AVG(gpa),
            AVG(gre),
            AVG(gre_v),
            AVG(gre_aw)
        FROM applicants;
        """
    )

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
    cursor.execute(
        """
        SELECT AVG(gpa)
        FROM applicants
        WHERE LOWER(term) = 'fall 2026'
          AND LOWER(TRIM(us_or_international)) = 'american'
          AND gpa IS NOT NULL;
        """
    )

    avg_gpa = cursor.fetchone()[0]

    print(f"Average GPA American Fall 2026: {avg_gpa:.2f}")
def question_5(cursor):
    cursor.execute(
        """
        SELECT
            100.0 *
            SUM(
                CASE
                    WHEN LOWER(status) LIKE '%accept%'
                    THEN 1
                    ELSE 0
                END
            )
            /
            COUNT(*)
        FROM applicants
        WHERE LOWER(term) = 'fall 2025';
        """
    )

    acceptance_percent = cursor.fetchone()[0]

    print(f"Fall 2025 acceptance percentage: {acceptance_percent:.2f}%")
def question_6(cursor):
    cursor.execute(
        """
        SELECT AVG(gpa)
        FROM applicants
        WHERE LOWER(term) = 'fall 2026'
          AND LOWER(status) LIKE '%accept%'
          AND gpa IS NOT NULL;
        """
    )

    avg_gpa = cursor.fetchone()[0]

    print(f"Average GPA accepted Fall 2026: {avg_gpa:.2f}")
def question_7(cursor):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE LOWER(program) LIKE '%computer science%'
          AND (
              LOWER(program) LIKE '%johns hopkins university%'
              OR LOWER(program) LIKE '%jhu%'
          )
          AND LOWER(degree) LIKE '%master%';
        """
    )

    count = cursor.fetchone()[0]

    print(f"JHU Computer Science master's count: {count}")
def question_8(cursor):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE LOWER(term) = 'fall 2026'
          AND LOWER(status) LIKE '%accept%'
          AND LOWER(degree) = 'phd'
          AND LOWER(program) LIKE '%computer science%'
          AND (
              LOWER(program) LIKE '%georgetown university%'
              OR LOWER(program) LIKE '%massachusetts institute of technology%'
              OR LOWER(program) LIKE '%mit%'
              OR LOWER(program) LIKE '%stanford university%'
              OR LOWER(program) LIKE '%carnegie mellon university%'
          );
        """
    )

    count = cursor.fetchone()[0]

    return count

def question_9(cursor, original_count):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM applicants
        WHERE LOWER(term) = 'fall 2026'
          AND LOWER(status) LIKE '%accept%'
          AND LOWER(degree) = 'phd'
          AND LOWER(llm_generated_program) LIKE '%computer science%'
          AND (
              LOWER(llm_generated_university) LIKE '%georgetown university%'
              OR LOWER(llm_generated_university) LIKE '%massachusetts institute of technology%'
              OR LOWER(llm_generated_university) LIKE '%mit%'
              OR LOWER(llm_generated_university) LIKE '%stanford university%'
              OR LOWER(llm_generated_university) LIKE '%carnegie mellon university%'
          );
        """
    )

    llm_count = cursor.fetchone()[0]
    difference = llm_count - original_count

    print(f"Original-field count: {original_count}")
    print(f"LLM-field count: {llm_count}")
    print(f"Difference: {difference:+d}")

def question_10(cursor):
    cursor.execute(
        """
        SELECT llm_generated_university, COUNT(*) AS application_count
        FROM applicants
        WHERE llm_generated_university IS NOT NULL
          AND TRIM(llm_generated_university) <> ''
        GROUP BY llm_generated_university
        ORDER BY application_count DESC
        LIMIT 5;
        """
    )

    results = cursor.fetchall()

    print("Top 5 universities by application count:")
    for university, count in results:
        print(f"{university}: {count}")

def question_11(cursor):
    cursor.execute(
        """
        SELECT AVG(gpa)
        FROM applicants
        WHERE LOWER(llm_generated_university) LIKE '%johns hopkins%';
        """
    )

    avg_gpa = cursor.fetchone()[0]

    print(f"Average GPA of Johns Hopkins University applicants: {avg_gpa:.2f}")

def get_applicant_summary(cursor):
    cursor.execute(
        """
        SELECT
            p_id,
            program,
            status,
            term,
            gpa
        FROM applicants
        LIMIT 1;
        """
    )

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
    connection = None

    try:
        connection = get_connection()

        with connection.cursor() as cursor:
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
            connection.close()


if __name__ == "__main__":  # pragma: no cover
    main()