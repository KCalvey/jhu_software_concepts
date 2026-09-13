from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple
from urllib.parse import urlparse


BASE_URL = "https://www.thegradcafe.com/survey/"


def build_url(page_number: int) -> str:
    """Build the GradCafe URL for a results page."""
    return f"{BASE_URL}?page={page_number}"


def capture_page_html(url: str, wait_seconds: float = 5.0) -> str:
    """
    Open a URL in a new Chrome tab, wait for it to load,
    capture that tab's HTML, then close it.
    """
    script = f'''
    tell application "Google Chrome"
        activate

        tell front window
            set newTab to make new tab with properties {{URL:"{url}"}}
            set active tab index to (count of tabs)
        end tell

        delay {wait_seconds}

        set pageHTML to execute newTab javascript "document.documentElement.outerHTML"

        close newTab

        return pageHTML
    end tell
    '''

    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout


def capture_page(page_number: int, wait_seconds: float = 5.0) -> Path:
    """
    Open a GradCafe results page, allow it to render,
    capture the HTML, and save it locally.
    """
    url = build_url(page_number)

    print(f"Opening page {page_number}: {url}")

    html = capture_page_html(url, wait_seconds)

    output_file = Path(f"page_{page_number}.html")
    output_file.write_text(html, encoding="utf-8")

    print(f"Saved {output_file}")

    return output_file


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="First GradCafe page to capture."
    )

    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of pages to capture."
    )

    args = parser.parse_args()

    for page_number in range(
        args.start_page,
        args.start_page + args.pages
    ):
        capture_page(page_number)


if __name__ == "__main__":
    main()