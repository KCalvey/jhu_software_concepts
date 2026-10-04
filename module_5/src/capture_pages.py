"""Capture and save GradCafe result pages for applicant data processing."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup


BASE_URL = "https://www.thegradcafe.com/"
START_URL = "https://www.thegradcafe.com/survey/"


def get_next_url(html: str):
    """
    Find the real GradCafe Next link, including its pagination cursor.
    """
    soup = BeautifulSoup(html, "html.parser")

    for link in soup.find_all("a", href=True):
        if link.get_text(" ", strip=True).lower() == "next":
            return urljoin(BASE_URL, link["href"])

    return None


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

def capture_page(
    page_number: int,
    url: str,
    wait_seconds: float = 5.0
):
    """
    Capture one GradCafe results page and save its HTML.
    """
    print(f"Opening page {page_number}: {url}")

    html = capture_page_html(url, wait_seconds)

    output_file = Path(f"page_{page_number}.html")
    output_file.write_text(html, encoding="utf-8")

    print(f"Saved {output_file}")

    return output_file, html

def main() -> None:
    """Parse command-line arguments and capture GradCafe result pages."""
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
    parser.add_argument(
        "--start-url",
        type=str,
        default=START_URL,
        help="Starting GradCafe results URL."
    )
    args = parser.parse_args()

    if args.start_page == 1:
        current_url = args.start_url
    else:
        previous_file = Path(f"page_{args.start_page - 1}.html")

        if not previous_file.exists():
            print(f"{previous_file} is missing.")
            sys.exit(1)

        previous_html = previous_file.read_text(encoding="utf-8")
        current_url = get_next_url(previous_html)

        if not current_url:
            print("Could not find the Next link in the previous page.")
            sys.exit(1)

    for page_number in range(
        args.start_page,
        args.start_page + args.pages
    ):
        if not current_url:
            print("No Next page found. Stopping.")
            break

        _, html = capture_page(page_number, current_url)
        current_url = get_next_url(html)

if __name__ == "__main__":  # pragma: no cover
    main()
