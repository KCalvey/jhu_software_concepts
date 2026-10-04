"""Provide the Flask web interface for applicant data analysis."""

# pylint: disable=not-callable

import subprocess
import sys
from pathlib import Path

from flask import Flask, render_template, request
from sqlalchemy import and_, func, or_, select

from models import Applicant, Session


app = Flask(__name__)
SCRAPE_PROCESS = None

MODULE_2_DIR = Path(__file__).resolve().parent.parent / "module_2"
MODULE_3_DIR = Path(__file__).resolve().parent


@app.route("/")
@app.route("/analysis")
def analysis():  # pylint: disable=too-many-locals,not-callable
    """Render the applicant analysis dashboard."""
    with Session() as session:
        fall_2026_count = session.scalar(
            select(func.count())
            .select_from(Applicant)
            .where(func.lower(Applicant.term) == "fall 2026")
            .limit(1)
        )

        avg_gpa_american = session.scalar(
            select(func.avg(Applicant.gpa)).where(
                and_(
                    func.lower(Applicant.term) == "fall 2026",
                    func.lower(func.trim(Applicant.us_or_international)) == "american",
                    Applicant.gpa.is_not(None),
                )
            )
            .limit(1)
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
            .limit(1)
        )

        avg_gpa = session.scalar(
            select(func.avg(Applicant.gpa)).limit(1)
        )

        avg_gre = session.scalar(
            select(func.avg(Applicant.gre)).limit(1)
        )

        avg_gre_v = session.scalar(
            select(func.avg(Applicant.gre_v)).limit(1)
        )

        avg_gre_aw = session.scalar(
            select(func.avg(Applicant.gre_aw)).limit(1)
        )

        total_fall_2025 = session.scalar(
            select(func.count())
            .select_from(Applicant)
            .where(func.lower(Applicant.term) == "fall 2025")
            .limit(1)
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
            .limit(1)
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
            .limit(1)
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
            .limit(1)
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
                        func.lower(
                            Applicant.program
                        ).like("%massachusetts institute of technology%"),
                        func.lower(Applicant.program).like("%mit%"),
                        func.lower(
                            Applicant.program
                        ).like("%stanford university%"),
                        func.lower(
                            Applicant.program
                        ).like("%carnegie mellon university%"),
                    ),
                )
            )
            .limit(1)
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
                        func.lower(
                            Applicant.llm_generated_university
                        ).like("%georgetown university%"),
                        func.lower(
                            Applicant.llm_generated_university
                        ).like("%massachusetts institute of technology%"),
                        func.lower(
                            Applicant.llm_generated_university
                        ).like("%mit%"),
                        func.lower(
                            Applicant.llm_generated_university
                        ).like("%stanford university%"),
                        func.lower(
                            Applicant.llm_generated_university
                        ).like("%carnegie mellon university%"),
                    ),
                )
            )
            .limit(1)
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
            .limit(1)
        )
        scrape_running = SCRAPE_PROCESS is not None and SCRAPE_PROCESS.poll() is None
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

@app.route("/update-analysis", methods=["POST"])
def update_analysis():
    """Report whether the analysis can be refreshed."""
    if SCRAPE_PROCESS is not None and SCRAPE_PROCESS.poll() is None:
        return {"busy": True}, 409

    return {"ok": True}, 200

@app.route("/pull-data", methods=["POST"])
def pull_data():  # pylint: disable=global-statement
    """Start the background data collection process."""
    global SCRAPE_PROCESS  # pylint: disable=global-statement

    if SCRAPE_PROCESS is not None and SCRAPE_PROCESS.poll() is None:
        return {"busy": True}, 409

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

    SCRAPE_PROCESS = subprocess.Popen(command)  # pylint: disable=consider-using-with

    return {"ok": True}, 202

if __name__ == "__main__":  # pragma: no cover
    app.run(debug=False)
