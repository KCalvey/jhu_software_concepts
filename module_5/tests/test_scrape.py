import json
import os
import sys

import pytest
from bs4 import BeautifulSoup

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

import scrape


@pytest.mark.scrape
def test_build_results_url():
    assert (
        scrape.build_results_url(3)
        == "https://www.thegradcafe.com/survey/?page=3"
    )


@pytest.mark.scrape
def test_check_robots_txt(monkeypatch):
    class FakeRobotParser:
        def __init__(self):
            self.url = None
            self.read_called = False

        def set_url(self, url):
            self.url = url

        def read(self):
            self.read_called = True

        def can_fetch(self, user_agent, target_url):
            assert user_agent == "*"
            assert target_url == "https://example.com/test"
            return True

    monkeypatch.setattr(scrape, "RobotFileParser", FakeRobotParser)

    result = scrape.check_robots_txt("https://example.com/test")

    assert result is True


@pytest.mark.scrape
def test_save_and_load_data(tmp_path):
    filename = tmp_path / "data.json"

    data = [
        {
            "program": "Computer Science",
            "university": "Johns Hopkins University",
        }
    ]

    scrape.save_data(data, filename)

    loaded = scrape.load_data(filename)

    assert loaded == data


@pytest.mark.scrape
def test_load_data_missing_file(tmp_path):
    filename = tmp_path / "missing.json"

    result = scrape.load_data(filename)

    assert result == []


@pytest.mark.scrape
def test_get_detail_value_found():
    html = """
    <dl>
        <dt>Undergrad GPA</dt>
        <dd>3.85</dd>
    </dl>
    """

    soup = BeautifulSoup(html, "html.parser")

    result = scrape._get_detail_value(soup, "Undergrad GPA")

    assert result == "3.85"


@pytest.mark.scrape
def test_get_detail_value_missing_label():
    soup = BeautifulSoup("<div>Nothing here</div>", "html.parser")

    assert scrape._get_detail_value(soup, "Undergrad GPA") is None


@pytest.mark.scrape
def test_get_detail_value_missing_dd():
    html = """
    <dl>
        <dt>Undergrad GPA</dt>
    </dl>
    """

    soup = BeautifulSoup(html, "html.parser")

    assert scrape._get_detail_value(soup, "Undergrad GPA") is None


@pytest.mark.scrape
def test_get_detail_value_not_provided():
    html = """
    <dl>
        <dt>GRE General</dt>
        <dd>Not Provided</dd>
    </dl>
    """

    soup = BeautifulSoup(html, "html.parser")

    assert scrape._get_detail_value(soup, "GRE General") is None


@pytest.mark.scrape
def test_get_detail_value_empty():
    html = """
    <dl>
        <dt>Notes</dt>
        <dd></dd>
    </dl>
    """

    soup = BeautifulSoup(html, "html.parser")

    assert scrape._get_detail_value(soup, "Notes") is None


@pytest.mark.scrape
@pytest.mark.parametrize(
    "value, expected",
    [
        (None, None),
        ("International Student", "International"),
        ("American", "American"),
        ("USA Citizen", "American"),
        ("Canadian", "Canadian"),
    ],
)
def test_normalize_student_type(value, expected):
    assert scrape._normalize_student_type(value) == expected


@pytest.mark.scrape
def test_parse_detail_page():
    html = """
    <dl>
        <dt>Notes</dt>
        <dd>Strong research experience</dd>

        <dt>Undergrad GPA</dt>
        <dd>3.90</dd>

        <dt>GRE General</dt>
        <dd>325</dd>

        <dt>GRE Verbal</dt>
        <dd>162</dd>

        <dt>Analytical Writing</dt>
        <dd>4.5</dd>

        <dt>Degree Type</dt>
        <dd>PhD</dd>

        <dt>Degree's Country of Origin</dt>
        <dd>International Student</dd>
    </dl>
    """

    result = scrape._parse_detail_page(html)

    assert result["comments"] == "Strong research experience"
    assert result["gpa"] == "3.90"
    assert result["gre"] == "325"
    assert result["gre_v"] == "162"
    assert result["gre_aw"] == "4.5"
    assert result["degree"] == "PhD"
    assert result["student_type"] == "International"


@pytest.mark.scrape
def test_parse_page_accepted(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    html = """
    <table>
        <tr>
            <td>Johns Hopkins University</td>
            <td>Computer Science PhD</td>
            <td>Sep 1, 2026</td>
            <td>Accepted on Sep 15, 2026</td>
            <td><a href="/result/123/">View</a></td>
        </tr>
    </table>
    """

    records = scrape._parse_page(html)

    assert len(records) == 1

    record = records[0]

    assert record["university"] == "Johns Hopkins University"
    assert record["program"] == "Computer Science"
    assert record["degree"] == "PhD"
    assert record["status"] == "Accepted"
    assert record["acceptance_date"] == "Sep 15, 2026"
    assert record["url"] == "https://www.thegradcafe.com/result/123/"


@pytest.mark.scrape
def test_parse_page_rejected(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    html = """
    <table>
        <tr>
            <td>Example University</td>
            <td>Data Science Masters</td>
            <td>Sep 2, 2026</td>
            <td>Rejected on Sep 20, 2026</td>
            <td><a href="/result/456/">View</a></td>
        </tr>
    </table>
    """

    records = scrape._parse_page(html)

    assert len(records) == 1
    assert records[0]["status"] == "Rejected"
    assert records[0]["rejection_date"] == "Sep 20, 2026"
    assert records[0]["degree"] == "Masters"


@pytest.mark.scrape
def test_parse_page_wait_listed(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    html = """
    <table>
        <tr>
            <td>Example University</td>
            <td>Statistics MS</td>
            <td>Sep 3, 2026</td>
            <td>Wait Listed</td>
            <td><a href="/result/789/">View</a></td>
        </tr>
    </table>
    """

    records = scrape._parse_page(html)

    assert len(records) == 1
    assert records[0]["status"] == "Wait listed"
    assert records[0]["degree"] == "MS"


@pytest.mark.scrape
def test_parse_page_generic_status(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    html = """
    <table>
        <tr>
            <td>Example University</td>
            <td>Physics MSc</td>
            <td>Sep 4, 2026</td>
            <td>Interview</td>
            <td><a href="/result/900/">View</a></td>
        </tr>
    </table>
    """

    records = scrape._parse_page(html)

    assert len(records) == 1
    assert records[0]["status"] == "Interview"
    assert records[0]["degree"] == "MSc"


@pytest.mark.scrape
def test_parse_page_skips_row_without_result_link(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    html = """
    <table>
        <tr>
            <td>A</td>
            <td>B</td>
            <td>C</td>
            <td>D</td>
            <td>E</td>
        </tr>
    </table>
    """

    assert scrape._parse_page(html) == []


@pytest.mark.scrape
def test_parse_page_skips_short_row(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    html = """
    <table>
        <tr>
            <td>Example University</td>
            <td>
                <a href="/result/111/">View</a>
            </td>
        </tr>
    </table>
    """

    assert scrape._parse_page(html) == []


@pytest.mark.scrape
def test_parse_page_detail_values(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    html = """
    <table>
        <tr>
            <td>Stanford University</td>
            <td>Computer Science</td>
            <td>Sep 1, 2026</td>
            <td>Accepted on Sep 10, 2026</td>
            <td><a href="/result/555/">View</a></td>
        </tr>

        <tr>
            <td colspan="5">
                <div>Fall 2026</div>
                <div>International</div>
                <div>GPA 3.91</div>
                <div>GRE V 165</div>
                <div>GRE AW 5.0</div>
                <div>GRE 330</div>
                <div>PhD</div>
                <div>Unknown badge</div>
            </td>
        </tr>
    </table>
    """

    records = scrape._parse_page(html)

    assert len(records) == 1

    record = records[0]

    assert record["term"] == "Fall 2026"
    assert record["student_type"] == "International"
    assert record["gpa"] == "GPA 3.91"
    assert record["gre_v"] == "GRE V 165"
    assert record["gre_aw"] == "GRE AW 5.0"
    assert record["gre"] == "GRE 330"
    assert record["degree"] == "PhD"


@pytest.mark.scrape
def test_parse_page_uses_saved_detail_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    detail_html = """
    <dl>
        <dt>Notes</dt>
        <dd>Saved detail comments</dd>

        <dt>Undergrad GPA</dt>
        <dd>3.88</dd>

        <dt>GRE General</dt>
        <dd>327</dd>

        <dt>GRE Verbal</dt>
        <dd>164</dd>

        <dt>Analytical Writing</dt>
        <dd>4.5</dd>

        <dt>Degree Type</dt>
        <dd>PhD</dd>

        <dt>Degree's Country of Origin</dt>
        <dd>American</dd>
    </dl>
    """

    (tmp_path / "result_777.html").write_text(
        detail_html,
        encoding="utf-8",
    )

    html = """
    <table>
        <tr>
            <td>Carnegie Mellon University</td>
            <td>Computer Science</td>
            <td>Sep 5, 2026</td>
            <td>Accepted on Sep 12, 2026</td>
            <td><a href="/result/777/">View</a></td>
        </tr>
    </table>
    """

    records = scrape._parse_page(html)

    assert len(records) == 1

    record = records[0]

    assert record["comments"] == "Saved detail comments"
    assert record["gpa"] == "3.88"
    assert record["gre"] == "327"
    assert record["gre_v"] == "164"
    assert record["gre_aw"] == "4.5"
    assert record["degree"] == "PhD"
    assert record["student_type"] == "American"