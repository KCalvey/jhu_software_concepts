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


def open_chrome_page(url: str) -> None:
    """Open a public GradCafe page in the user's normal Chrome browser."""
    subprocess.run(
        ["open", "-a", "Google Chrome", url],
        check=True
    )


def capture_current_html() -> str:
    """
    Capture the rendered HTML from Chrome's active tab.
    """
    script = '''
    tell application "Google Chrome"
        set pageHTML to execute active tab of front window javascript "document.documentElement.outerHTML"
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


def close_current_tab() -> None:
    """Close Chrome's active tab after capture."""
    script = '''
    tell application "Google Chrome"
        close active tab of front window
    end tell
    '''

    subprocess.run(
        ["osascript", "-e", script],
        check=True
    )


def capture_page(page_number: int, wait_seconds: float = 5.0) -> Path:
    """
    Open a GradCafe results page, allow it to render,
    capture the HTML, and save it locally.
    """
    url = build_url(page_number)

    print(f"Opening page {page_number}: {url}")

    open_chrome_page(url)

    time.sleep(wait_seconds)

    html = capture_current_html()

    output_file = Path(f"page_{page_number}.html")
    output_file.write_text(html, encoding="utf-8")

    print(f"Saved {output_file}")

    close_current_tab()

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