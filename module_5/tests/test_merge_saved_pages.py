import os
import sys

import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

import merge_saved_pages


class FakePage:
    def __init__(self, name, html):
        self.name = name
        self._html = html
        self.stem = name.replace(".html", "")

    def read_text(self, encoding="utf-8"):
        return self._html


class FakeFolder:
    def __init__(self, pages):
        self.pages = pages

    def glob(self, pattern):
        return self.pages


@pytest.mark.db
def test_merge_folder_adds_only_new_records(monkeypatch, capsys):
    existing = [
        {"url": "https://example.com/result/1"}
    ]

    page1 = FakePage("page_1.html", "<html>page1</html>")
    page2 = FakePage("page_2.html", "<html>page2</html>")

    fake_folder = FakeFolder([page2, page1])

    monkeypatch.setattr(
        merge_saved_pages,
        "Path",
        lambda folder_name: fake_folder
    )

    monkeypatch.setattr(
        merge_saved_pages,
        "load_data",
        lambda: existing.copy()
    )

    def fake_parse_page(html):
        if html == "<html>page1</html>":
            return [
                {"url": "https://example.com/result/1"},
                {"url": "https://example.com/result/2"},
            ]

        return [
            {"url": "https://example.com/result/2"},
            {"url": "https://example.com/result/3"},
            {"url": None},
        ]

    monkeypatch.setattr(
        merge_saved_pages,
        "_parse_page",
        fake_parse_page
    )

    saved = []

    def fake_save_data(records):
        saved.clear()
        saved.extend(records)

    monkeypatch.setattr(
        merge_saved_pages,
        "save_data",
        fake_save_data
    )

    result = merge_saved_pages.merge_folder("fake_pages")

    assert result == 4

    urls = [record.get("url") for record in saved]

    assert "https://example.com/result/1" in urls
    assert "https://example.com/result/2" in urls
    assert "https://example.com/result/3" in urls
    assert None in urls

    output = capsys.readouterr().out

    assert "Processing fake_pages: 2 pages" in output
    assert "page_1.html" in output
    assert "page_2.html" in output
    assert "Added from fake_pages:" in output


@pytest.mark.db
def test_merge_folder_no_pages(monkeypatch, capsys):
    fake_folder = FakeFolder([])

    monkeypatch.setattr(
        merge_saved_pages,
        "Path",
        lambda folder_name: fake_folder
    )

    monkeypatch.setattr(
        merge_saved_pages,
        "load_data",
        lambda: [{"url": "existing"}]
    )

    saved = []

    monkeypatch.setattr(
        merge_saved_pages,
        "save_data",
        lambda records: saved.extend(records)
    )

    result = merge_saved_pages.merge_folder("empty_pages")

    assert result == 1

    output = capsys.readouterr().out
    assert "Processing empty_pages: 0 pages" in output
    assert "Added from empty_pages: 0" in output


@pytest.mark.db
def test_main(monkeypatch, capsys):
    calls = []

    def fake_merge_folder(folder_name):
        calls.append(folder_name)

        if folder_name == "fall24_pages":
            return 10

        return 20

    monkeypatch.setattr(
        merge_saved_pages,
        "merge_folder",
        fake_merge_folder
    )

    merge_saved_pages.main()

    assert calls == [
        "fall24_pages",
        "fall23_pages",
    ]

    output = capsys.readouterr().out
    assert "FINAL TOTAL: 20" in output