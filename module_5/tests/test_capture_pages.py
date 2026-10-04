import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

import capture_pages


@pytest.mark.web
def test_get_next_url_relative():
    html = """
    <html>
        <body>
            <a href="/survey/?page=2">Next</a>
        </body>
    </html>
    """

    result = capture_pages.get_next_url(html)

    assert result == "https://www.thegradcafe.com/survey/?page=2"


@pytest.mark.web
def test_get_next_url_none():
    html = """
    <html>
        <body>
            <a href="/survey/">Previous</a>
        </body>
    </html>
    """

    assert capture_pages.get_next_url(html) is None


@pytest.mark.web
def test_capture_page_html(monkeypatch):
    fake_result = SimpleNamespace(stdout="<html>test page</html>")

    def fake_run(*args, **kwargs):
        return fake_result

    monkeypatch.setattr(capture_pages.subprocess, "run", fake_run)

    result = capture_pages.capture_page_html(
        "https://example.com",
        wait_seconds=0
    )

    assert result == "<html>test page</html>"


@pytest.mark.web
def test_capture_page(monkeypatch, tmp_path):
    html = "<html><body>GradCafe</body></html>"

    monkeypatch.setattr(
        capture_pages,
        "capture_page_html",
        lambda url, wait_seconds=5.0: html
    )

    monkeypatch.chdir(tmp_path)

    output_file, result_html = capture_pages.capture_page(
        3,
        "https://example.com/page3",
        wait_seconds=0
    )

    assert output_file == Path("page_3.html")
    assert result_html == html
    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == html


@pytest.mark.web
def test_main_start_page_one(monkeypatch):
    args = SimpleNamespace(
        start_page=1,
        pages=1,
        start_url="https://example.com/start"
    )

    monkeypatch.setattr(
        capture_pages.argparse.ArgumentParser,
        "parse_args",
        lambda self: args
    )

    calls = []

    def fake_capture(page_number, url):
        calls.append((page_number, url))
        return Path(f"page_{page_number}.html"), """
        <a href="/survey/page2">Next</a>
        """

    monkeypatch.setattr(capture_pages, "capture_page", fake_capture)

    capture_pages.main()

    assert calls == [(1, "https://example.com/start")]


@pytest.mark.web
def test_main_uses_previous_page(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    previous = tmp_path / "page_1.html"
    previous.write_text(
        '<a href="/survey/page2">Next</a>',
        encoding="utf-8"
    )

    args = SimpleNamespace(
        start_page=2,
        pages=1,
        start_url="https://example.com/start"
    )

    monkeypatch.setattr(
        capture_pages.argparse.ArgumentParser,
        "parse_args",
        lambda self: args
    )

    calls = []

    def fake_capture(page_number, url):
        calls.append((page_number, url))
        return Path(f"page_{page_number}.html"), """
        <a href="/survey/page3">Next</a>
        """

    monkeypatch.setattr(capture_pages, "capture_page", fake_capture)

    capture_pages.main()

    assert len(calls) == 1
    assert calls[0][0] == 2
    assert "page2" in calls[0][1]


@pytest.mark.web
def test_main_missing_previous_page(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    args = SimpleNamespace(
        start_page=2,
        pages=1,
        start_url="https://example.com/start"
    )

    monkeypatch.setattr(
        capture_pages.argparse.ArgumentParser,
        "parse_args",
        lambda self: args
    )

    with pytest.raises(SystemExit) as exc:
        capture_pages.main()

    assert exc.value.code == 1


@pytest.mark.web
def test_main_previous_page_has_no_next(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    previous = tmp_path / "page_1.html"
    previous.write_text(
        "<html><body>No next link</body></html>",
        encoding="utf-8"
    )

    args = SimpleNamespace(
        start_page=2,
        pages=1,
        start_url="https://example.com/start"
    )

    monkeypatch.setattr(
        capture_pages.argparse.ArgumentParser,
        "parse_args",
        lambda self: args
    )

    with pytest.raises(SystemExit) as exc:
        capture_pages.main()

    assert exc.value.code == 1

@pytest.mark.web
def test_main_stops_when_no_next_page(monkeypatch):
    args = SimpleNamespace(
        start_page=1,
        pages=2,
        start_url="https://example.com/start"
    )

    monkeypatch.setattr(
        capture_pages.argparse.ArgumentParser,
        "parse_args",
        lambda self: args
    )

    calls = []

    def fake_capture(page_number, url):
        calls.append((page_number, url))
        return Path(f"page_{page_number}.html"), "<html>No next link</html>"

    monkeypatch.setattr(capture_pages, "capture_page", fake_capture)

    capture_pages.main()

    assert len(calls) == 1