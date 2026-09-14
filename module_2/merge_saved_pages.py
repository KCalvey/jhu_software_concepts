import json
from pathlib import Path

from scrape import _parse_page, load_data, save_data


def merge_folder(folder_name):
    all_records = load_data()

    existing_urls = {
        record.get("url")
        for record in all_records
        if record.get("url")
    }

    folder = Path(folder_name)

    page_files = sorted(
        folder.glob("page_*.html"),
        key=lambda p: int(p.stem.split("_")[1])
    )

    print(f"\nProcessing {folder_name}: {len(page_files)} pages")

    added = 0

    for page_file in page_files:
        html = page_file.read_text(encoding="utf-8")
        records = _parse_page(html)

        new_records = [
            record
            for record in records
            if record.get("url") not in existing_urls
        ]

        for record in new_records:
            if record.get("url"):
                existing_urls.add(record["url"])

        all_records.extend(new_records)
        added += len(new_records)

        save_data(all_records)

        print(
            f"{page_file.name}: "
            f"{len(new_records)} new | "
            f"{len(all_records)} total"
        )

    print(f"\nAdded from {folder_name}: {added}")
    return len(all_records)


def main():
    merge_folder("fall24_pages")
    final_total = merge_folder("fall23_pages")

    print(f"\nFINAL TOTAL: {final_total}")


if __name__ == "__main__":
    main()
