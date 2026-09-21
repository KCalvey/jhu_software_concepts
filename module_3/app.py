from flask import Flask, render_template, redirect, url_for, request
from sqlalchemy import select, func, and_, or_
import subprocess
import sys
from pathlib import Path
import shutil

from models import Applicant, Session


app = Flask(__name__)
scrape_process = None

MODULE_2_DIR = Path(__file__).resolve().parent.parent / "module_2"
MODULE_3_DIR = Path(__file__).resolve().parent


@app.route("/")
def analysis():
    with Session() as session:
        fall_2026_count = session.scalar(
            select(func.count())
            .select_from(Applicant)
            .where(func.lower(Applicant.term) == "fall 2026")
        )

        avg_gpa_american = session.scalar(
            select(func.avg(Applicant.gpa)).where(
                and_(
                    func.lower(Applicant.term) == "fall 2026",
                    func.lower(func.trim(Applicant.us_or_international)) == "american",
                    Applicant.gpa.is_not(None),
                )
            )
        )
        percent_international = session.scalar(
            select(
                100.0
                * func.count().filter(
                    func.lower(func.trim(Applicant.us_or_international))
                    == "international"
                )
                / func.nullif(func.count(), 0)
            )
            .select_from(Applicant)
            .where(
                and_(
                    Applicant.us_or_international.is_not(None),
                    func.trim(Applicant.us_or_international) != "",
                )
            )
        )

        avg_gpa = session.scalar(
            select(func.avg(Applicant.gpa))
        )

        avg_gre = session.scalar(
            select(func.avg(Applicant.gre))
        )

        avg_gre_v = session.scalar(
            select(func.avg(Applicant.gre_v))
        )

        avg_gre_aw = session.scalar(
            select(func.avg(Applicant.gre_aw))
        )

        total_fall_2025 = session.scalar(
            select(func.count())
            .select_from(Applicant)
            .where(func.lower(Applicant.term) == "fall 2025")
        )

        accepted_fall_2025 = session.scalar(
            select(func.count())
            .select_from(Applicant)
            .where(
                and_(
                    func.lower(Applicant.term) == "fall 2025",
                    func.lower(Applicant.status).like("%accept%"),
                )
            )
        )

        fall_2025_acceptance_percent = (
            100.0 * accepted_fall_2025 / total_fall_2025
        )

        avg_gpa_accepted_fall_2026 = session.scalar(
            select(func.avg(Applicant.gpa)).where(
                and_(
                    func.lower(Applicant.term) == "fall 2026",
                    func.lower(Applicant.status).like("%accept%"),
                    Applicant.gpa.is_not(None),
                )
            )
        )

        jhu_masters_count = session.scalar(
            select(func.count())
            .select_from(Applicant)
            .where(
                and_(
                    func.lower(Applicant.program).like("%computer science%"),
                    or_(
                        func.lower(Applicant.program).like("%johns hopkins university%"),
                        func.lower(Applicant.program).like("%jhu%"),
                    ),
                    func.lower(Applicant.degree).like("%master%"),
                )
            )
        )

        original_field_count = session.scalar(
            select(func.count())
            .select_from(Applicant)
            .where(
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
        )

        llm_field_count = session.scalar(
            select(func.count())
            .select_from(Applicant)
            .where(
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
        )

        difference = llm_field_count - original_field_count

        top_universities = session.execute(
            select(
                Applicant.llm_generated_university,
                func.count().label("application_count"),
            )
            .where(
                and_(
                    Applicant.llm_generated_university.is_not(None),
                    func.trim(Applicant.llm_generated_university) != "",
                )
            )
            .group_by(Applicant.llm_generated_university)
            .order_by(func.count().desc())
            .limit(5)
        ).all()

        jhu_avg_gpa = session.scalar(
            select(func.avg(Applicant.gpa)).where(
                func.lower(Applicant.llm_generated_university).like("%johns hopkins%")
            )
        )
        scrape_running = scrape_process is not None and scrape_process.poll() is None
        status = request.args.get("status")

    return render_template(
        "analysis.html",
        fall_2026_count=fall_2026_count,
        avg_gpa_american=avg_gpa_american,
        percent_international=percent_international,
        avg_gpa=avg_gpa,
        avg_gre=avg_gre,
        avg_gre_v=avg_gre_v,
        avg_gre_aw=avg_gre_aw,
        fall_2025_acceptance_percent=fall_2025_acceptance_percent,
        avg_gpa_accepted_fall_2026=avg_gpa_accepted_fall_2026,
        jhu_masters_count=jhu_masters_count,
        original_field_count=original_field_count,
        llm_field_count=llm_field_count,
        difference=difference,
        top_universities=top_universities,
        jhu_avg_gpa=jhu_avg_gpa,
        scrape_running=scrape_running,
        status=status,
    )

@app.route("/update-analysis")
def update_analysis():
    if scrape_process is not None and scrape_process.poll() is None:
        return redirect(url_for("analysis", status="retrieving"))

    return redirect(url_for("analysis", status="updated"))

@app.route("/pull-data", methods=["POST"])
def pull_data():
    global scrape_process

    if scrape_process is not None and scrape_process.poll() is None:
        return redirect(url_for("analysis"))

    command = [
        sys.executable,
        "-c",
        f"""
import subprocess
import sys
import shutil

subprocess.run(
    [sys.executable, "capture_pages.py", "--start-page", "1", "--pages", "5"],
    cwd=r"{MODULE_2_DIR}",
    check=True,
)

subprocess.run(
    [sys.executable, "scrape.py", "--start-page", "1", "--pages", "5"],
    cwd=r"{MODULE_2_DIR}",
    check=True,
)

shutil.copy2(
    r"{MODULE_2_DIR}/applicant_data.json",
    r"{MODULE_3_DIR}/applicant_data.json"
)

subprocess.run(
    [sys.executable, "clean.py"],
    cwd=r"{MODULE_3_DIR}",
    check=True,
)

subprocess.run(
    [sys.executable, "load_data.py"],
    cwd=r"{MODULE_3_DIR}",
    check=True,
)
""",
    ]

    scrape_process = subprocess.Popen(command)

    return redirect(url_for("analysis"))

if __name__ == "__main__":
    app.run(debug=True)