import json
from pathlib import Path

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser


BASE_URL = "https://www.thegradcafe.com/"
ROBOTS_URL = urljoin(BASE_URL, "robots.txt")


def check_robots_txt(target_url):
    """
    Check whether robots.txt allows access to the target URL.
    """
    robot_parser = RobotFileParser()
    robot_parser.set_url(ROBOTS_URL)
    robot_parser.read()

    return robot_parser.can_fetch("*", target_url)


def build_results_url(page_number=1):
    """
    Build a GradCafe results URL for a specific page.
    """
    return urljoin(BASE_URL, f"survey/?page={page_number}")
    
def save_data(data, filename="applicant_data.json"):
    """
    Save applicant data to a JSON file.
    """
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_data(filename="applicant_data.json"):
    """
    Load applicant data from a JSON file.
    """
    path = Path(filename)

    if not path.exists():
        return []

    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def _parse_page(html):
    """
    Parse applicant records from rendered GradCafe HTML.
    """
    soup = BeautifulSoup(html, "html.parser")
    records = []

    rows = soup.find_all("tr")

    for index, row in enumerate(rows):
        # A main applicant row contains a link to /result/...
        result_link = row.find(
            "a",
            href=lambda href: href and "/result/" in href
        )

        if not result_link:
            continue

        cells = row.find_all("td")

        # Applicant rows should contain the main five table cells
        if len(cells) < 5:
            continue

        university = cells[0].get_text(" ", strip=True)
        program_text = cells[1].get_text(" ", strip=True)
        date_added = cells[2].get_text(" ", strip=True)
        status_text = cells[3].get_text(" ", strip=True)

        record = {
            "program": program_text,
            "university": university,
            "comments": None,
            "date_added": date_added,
            "url": urljoin(BASE_URL, result_link["href"]),
            "status": None,
            "acceptance_date": None,
            "rejection_date": None,
            "term": None,
            "student_type": None,
            "gre": None,
            "gre_v": None,
            "gre_aw": None,
            "gpa": None,
            "degree": None,
            "raw_text": row.get_text(" ", strip=True),
        }

        # Parse applicant status
        lower_status = status_text.lower()

        if "accepted on" in lower_status:
            record["status"] = "Accepted"
            record["acceptance_date"] = status_text.replace(
                "Accepted on ", ""
            ).strip()

        elif "rejected on" in lower_status:
            record["status"] = "Rejected"
            record["rejection_date"] = status_text.replace(
                "Rejected on ", ""
            ).strip()

        elif "wait listed" in lower_status:
            record["status"] = "Wait listed"

        elif status_text:
            record["status"] = status_text

        # Try to identify the degree from the program text
        degree_names = [
            "PhD",
            "Masters",
            "Master's",
            "MFA",
            "MA",
            "MS",
            "MSc",
        ]

        for degree in degree_names:
            if program_text.endswith(degree):
                record["degree"] = degree
                record["program"] = program_text[:-len(degree)].strip()
                break

        # Look at the following row for additional applicant details
        if index + 1 < len(rows):
            detail_row = rows[index + 1]

            detail_values = [
                div.get_text(" ", strip=True)
                for div in detail_row.find_all("div")
                if div.get_text(" ", strip=True)
            ]

            for value in detail_values:
                lower_value = value.lower()

                if value.startswith(
                    ("Fall ", "Spring ", "Summer ", "Winter ")
                ):
                    record["term"] = value

                elif value in ("International", "American"):
                    record["student_type"] = value

                elif value.startswith("GPA"):
                    record["gpa"] = value

                elif value.startswith("GRE V"):
                    record["gre_v"] = value

                elif value.startswith("GRE AW"):
                    record["gre_aw"] = value

                elif value.startswith("GRE"):
                    record["gre"] = value

                elif value in ("Masters", "PhD"):
                    record["degree"] = value

                elif (
                    "accepted on" not in lower_value
                    and "rejected on" not in lower_value
                    and "wait listed" not in lower_value
                ):
                    # Do not assign unknown badge text automatically.
                    pass

        records.append(record)

    return records

def main():
    all_records = load_data()

    existing_urls = {
        record["url"]
        for record in all_records
        if record.get("url")
    }

    print(f"Starting with {len(all_records)} existing records.")

    page_number = 1

    while True:
        test_url = build_results_url(page_number)
        print(f"\nProcessing page {page_number}: {test_url}")

        if not check_robots_txt(test_url):
            print("robots.txt does not allow access to this URL.")
            break

        page_file = Path(f"page_{page_number}.html")

        if not page_file.exists():
            print(f"{page_file} not found. Stopping here.")
            break

        with open(page_file, "r", encoding="utf-8") as file:
            html = file.read()

        page_records = _parse_page(html)

        new_records = [
            record
            for record in page_records
            if record.get("url") not in existing_urls
        ]

        for record in new_records:
            if record.get("url"):
                existing_urls.add(record["url"])

        all_records.extend(new_records)

        save_data(all_records)

        print(f"Records found on page: {len(page_records)}")
        print(f"New records added: {len(new_records)}")
        print(f"Total saved records: {len(all_records)}")

        page_number += 1

    loaded_records = load_data()
    print(f"\nFinal records reloaded from JSON: {len(loaded_records)}")

if __name__ == "__main__":
    main()
