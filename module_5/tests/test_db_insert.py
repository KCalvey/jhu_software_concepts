import os
import sys
from unittest import result

import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

import load_data


@pytest.mark.db
def test_extract_p_id():
    url = "https://www.thegradcafe.com/result/123456/"
    assert load_data.extract_p_id(url) == 123456


@pytest.mark.db
def test_extract_p_id_missing():
    assert load_data.extract_p_id(None) is None
    assert load_data.extract_p_id("") is None
    assert load_data.extract_p_id("https://example.com/test") is None


@pytest.mark.db
def test_clean_float():
    assert load_data.clean_float("GPA 3.75", "GPA") == 3.75
    assert load_data.clean_float("GRE 165", "GRE") == 165.0
    assert load_data.clean_float(None) is None
    assert load_data.clean_float("not-a-number") is None


@pytest.mark.db
def test_create_table_uses_required_schema():
    class FakeCursor:
        def __init__(self):
            self.sql = None

        def execute(self, sql):
            self.sql = sql

    cursor = FakeCursor()

    load_data.create_table(cursor)
    sql_text = cursor.sql.as_string(None)

    assert "CREATE TABLE IF NOT EXISTS applicants" in sql_text
    assert "p_id INTEGER PRIMARY KEY" in sql_text
    assert "program TEXT" in sql_text
    assert "url TEXT" in sql_text
    assert "status TEXT" in sql_text
    assert "term TEXT" in sql_text
    assert "gpa FLOAT" in sql_text

    @pytest.mark.db
    def test_query_returns_expected_dictionary():
        import query_data

        class FakeCursor:
            def execute(self, sql):
                self.sql = sql

            def fetchone(self):
                return (
                    123456,
                    "Computer Science, Johns Hopkins University",
                    "Accepted",
                    "Fall 2026",
                    3.82,
                )

        result = query_data.get_applicant_summary(FakeCursor())

        assert isinstance(result, dict)

        assert set(result.keys()) == {
            "p_id",
            "program",
            "status",
            "term",
            "gpa",
        }

        assert result["p_id"] == 123456
        assert result["status"] == "Accepted"

@pytest.mark.db
def test_clean_date():
    assert load_data.clean_date("Sep 27, 2026").isoformat() == "2026-09-27"
    assert load_data.clean_date(None) is None
    assert load_data.clean_date("") is None
    assert load_data.clean_date("not-a-date") is None


@pytest.mark.db
def test_get_connection(monkeypatch):
    monkeypatch.setenv("DB_NAME", "module3_db")
    monkeypatch.setenv("DB_USER", "karicalvey")
    monkeypatch.setenv("DB_PASSWORD", "test_password")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "5432")

    called = {}

    def fake_connect(**kwargs):
        called.update(kwargs)
        return "fake-connection"

    monkeypatch.setattr(load_data.psycopg, "connect", fake_connect)

    result = load_data.get_connection()

    assert result == "fake-connection"
    assert called["dbname"] == "module3_db"
    assert called["user"] == "karicalvey"
    assert called["host"] == "localhost"
    assert called["port"] == "5432"

@pytest.mark.db
def test_load_data_success(tmp_path, monkeypatch, capsys):
    import json

    test_file = tmp_path / "test_data.json"

    test_records = [
        {
            "url": "https://www.thegradcafe.com/result/123456/",
            "program": "Computer Science",
            "university": "Johns Hopkins University",
            "comments": "Test applicant",
            "date_added": "Sep 27, 2026",
            "status": "Accepted",
            "term": "Fall 2026",
            "student_type": "American",
            "gpa": "GPA 3.82",
            "gre": "GRE 165",
            "gre_v": "GRE V 160",
            "gre_aw": "GRE AW 4.5",
            "degree": "Masters",
            "standardized_program": "Computer Science",
            "standardized_university": "Johns Hopkins University",
        },
        {
            "url": "invalid-url"
        },
    ]

    test_file.write_text(json.dumps(test_records))

    monkeypatch.setattr(load_data, "DATA_FILE", str(test_file))

    class FakeCursor:
        def __init__(self):
            self.rowcount = 1

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def execute(self, sql, values=None):
            self.rowcount = 1

    class FakeConnection:
        def __init__(self):
            self.committed = False
            self.closed = False

        def cursor(self):
            return FakeCursor()

        def commit(self):
            self.committed = True

        def rollback(self):
            pass

        def close(self):
            self.closed = True

    fake_connection = FakeConnection()

    monkeypatch.setattr(
        load_data,
        "get_connection",
        lambda: fake_connection,
    )

    load_data.load_data()

    output = capsys.readouterr().out

    assert "Successfully processed 2 records." in output
    assert "New records inserted: 1" in output
    assert fake_connection.committed is True
    assert fake_connection.closed is True

@pytest.mark.db
def test_load_data_error(tmp_path, monkeypatch, capsys):
    import json

    test_file = tmp_path / "test_data.json"
    test_file.write_text(json.dumps([]))

    monkeypatch.setattr(load_data, "DATA_FILE", str(test_file))

    class FakeCursor:
        def __enter__(self):
            raise ValueError("database test error")

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    class FakeConnection:
        def __init__(self):
            self.rolled_back = False
            self.closed = False

        def cursor(self):
            return FakeCursor()

        def rollback(self):
            self.rolled_back = True

        def close(self):
            self.closed = True

    fake_connection = FakeConnection()

    monkeypatch.setattr(
        load_data,
        "get_connection",
        lambda: fake_connection,
    )

    load_data.load_data()

    output = capsys.readouterr().out

    assert "Error loading data: database test error" in output
    assert fake_connection.rolled_back is True
    assert fake_connection.closed is True
    