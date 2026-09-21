from sqlalchemy import select, func, and_, or_

from models import Applicant, Session

def question_1(session):
    stmt = select(func.count()).select_from(Applicant).where(
        func.lower(Applicant.term) == "fall 2026"
    )

    count = session.scalar(stmt)

    print(f"Fall 2026 applicant count: {count}")

def question_4(session):
    stmt = select(func.avg(Applicant.gpa)).where(
        and_(
            func.lower(Applicant.term) == "fall 2026",
            func.lower(func.trim(Applicant.us_or_international)) == "american",
            Applicant.gpa.is_not(None),
        )
    )

    avg_gpa = session.scalar(stmt)

    print(f"Average GPA American Fall 2026: {avg_gpa:.2f}")

def question_5(session):
    total_stmt = select(func.count()).select_from(Applicant).where(
        func.lower(Applicant.term) == "fall 2025"
    )

    accepted_stmt = select(func.count()).select_from(Applicant).where(
        and_(
            func.lower(Applicant.term) == "fall 2025",
            func.lower(Applicant.status).like("%accept%"),
        )
    )

    total = session.scalar(total_stmt)
    accepted = session.scalar(accepted_stmt)

    acceptance_percent = 100.0 * accepted / total

    print(f"Fall 2025 acceptance percentage: {acceptance_percent:.2f}%")

def question_8(session):
    stmt = select(func.count()).select_from(Applicant).where(
        and_(
        func.lower(Applicant.term) == "fall 2026",
        func.lower(Applicant.status).like("%accept%"),
        func.lower(Applicant.degree) == "phd",
        func.lower(Applicant.program).like("%computer science%"),
        or_(
            func.lower(Applicant.program).like("%georgetown university%"),
            func.lower(Applicant.program).like("%massachusetts institute of technology%"),
            func.lower(Applicant.program).like("%mit%"),
            func.lower(Applicant.program).like("%stanford university%"),
            func.lower(Applicant.program).like("%carnegie mellon university%"),
        ),
    )
)

    count = session.scalar(stmt)

    print(f"Original-field count: {count}")

    return count

def question_9(session, original_count):
    stmt = select(func.count()).select_from(Applicant).where(
        and_(
            func.lower(Applicant.term) == "fall 2026",
            func.lower(Applicant.status).like("%accept%"),
            func.lower(Applicant.degree) == "phd",
            func.lower(Applicant.llm_generated_program).like("%computer science%"),
            or_(
                func.lower(Applicant.llm_generated_university).like("%georgetown university%"),
                func.lower(Applicant.llm_generated_university).like("%massachusetts institute of technology%"),
                func.lower(Applicant.llm_generated_university).like("%mit%"),
                func.lower(Applicant.llm_generated_university).like("%stanford university%"),
                func.lower(Applicant.llm_generated_university).like("%carnegie mellon university%"),
            ),
        )
    )

    llm_count = session.scalar(stmt)
    difference = llm_count - original_count

    print(f"LLM-field count: {llm_count}")
    print(f"Difference: {difference:+d}")

def question_11(session):
    stmt = select(func.avg(Applicant.gpa)).where(
        func.lower(Applicant.llm_generated_university).like("%johns hopkins%")
    )

    avg_gpa = session.scalar(stmt)

    print(f"Average GPA of Johns Hopkins University applicants: {avg_gpa:.2f}")

def main():
    with Session() as session:
        question_1(session)
        question_4(session)
        question_5(session)

        original_count = question_8(session)
        question_9(session, original_count)
        question_11(session)
        
if __name__ == "__main__":
    main()
