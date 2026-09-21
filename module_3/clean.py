import json
import re
from html import unescape

INPUT_FILE = "applicant_data.json"
OUTPUT_FILE = "llm_extend_applicant_data.json"


def _clean_text(value):
    if value is None:
        return None

    value = unescape(str(value))
    value = re.sub(r"<[^>]+>", "", value)
    value = re.sub(r"\s+", " ", value).strip()

    return value if value else None


def clean_data(records):
    cleaned_records = []

    for record in records:
        cleaned = dict(record)

        cleaned["program"] = _clean_text(record.get("program"))
        cleaned["university"] = _clean_text(record.get("university"))
        cleaned["comments"] = _clean_text(record.get("comments"))
        cleaned["raw_program"] = record.get(
            "raw_program",
            record.get("program")
        )

        # Preserve original values while providing standardized fields.
        cleaned["standardized_program"] = cleaned["program"]
        cleaned["standardized_university"] = cleaned["university"]

        cleaned_records.append(cleaned)

    return cleaned_records


def load_data():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(records):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, ensure_ascii=False)


def main():
    records = load_data()
    cleaned_records = clean_data(records)
    save_data(cleaned_records)

    print(f"Cleaned {len(cleaned_records)} records.")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
