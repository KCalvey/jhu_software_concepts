import os
import sys

import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")),
)

import query_data


class FakeCursor:
    def __init__(self, fetchone_values=None, fetchall_values=None):
        self.fetchone_values = fetchone_values or []
        self.fetchall_values = fetchall_values or []
        self.fetchone_index = 0
        self.executed = []

    def execute(self, query):
        self.executed.append(query)

    def fetchone(self):
        if self.fetchone_index >= len(self.fetchone_values):
            return None

        value = self.fetchone_values[self.fetchone_index]
        self.fetchone_index += 1
        return value

    def fetchall(self):
        return self.fetchall_values


@pytest.mark.db
def test_question_1(capsys):
    cursor = FakeCursor(fetchone_values=[(25,)])

    query_data.question_1(cursor)

    output = capsys.readouterr().out
    assert "Fall 2026 applicant count: 25" in output


@pytest.mark.analysis
def test_question_2_with_result(capsys):
    cursor = FakeCursor(fetchone_values=[(39.284,)])

    query_data.question_2(cursor)

    output = capsys.readouterr().out
    assert "Percent international: 39.28%" in output


@pytest.mark.analysis
def test_question_2_no_result(capsys):
    cursor = FakeCursor(fetchone_values=[None])

    query_data.question_2(cursor)

    output = capsys.readouterr().out
    assert "no result returned" in output


@pytest.mark.analysis
def test_question_3(capsys):
    cursor = FakeCursor(
        fetchone_values=[(3.75, 165.4, 158.2, 4.6)]
    )

    query_data.question_3(cursor)

    output = capsys.readouterr().out

    assert "Average GPA: 3.75" in output
    assert "Average GRE Quantitative: 165.40" in output
    assert "Average GRE Verbal: 158.20" in output
    assert "Average GRE Analytical Writing: 4.60" in output


@pytest.mark.analysis
def test_question_3_no_result(capsys):
    cursor = FakeCursor(fetchone_values=[None])

    query_data.question_3(cursor)

    output = capsys.readouterr().out
    assert "Question 3: no result returned" in output


@pytest.mark.analysis
def test_question_4(capsys):
    cursor = FakeCursor(fetchone_values=[(3.81,)])

    query_data.question_4(cursor)

    output = capsys.readouterr().out
    assert "Average GPA American Fall 2026: 3.81" in output


@pytest.mark.analysis
def test_question_5(capsys):
    cursor = FakeCursor(fetchone_values=[(42.567,)])

    query_data.question_5(cursor)

    output = capsys.readouterr().out
    assert "Fall 2025 acceptance percentage: 42.57%" in output


@pytest.mark.analysis
def test_question_6(capsys):
    cursor = FakeCursor(fetchone_values=[(3.92,)])

    query_data.question_6(cursor)

    output = capsys.readouterr().out
    assert "Average GPA accepted Fall 2026: 3.92" in output


@pytest.mark.analysis
def test_question_7(capsys):
    cursor = FakeCursor(fetchone_values=[(12,)])

    query_data.question_7(cursor)

    output = capsys.readouterr().out
    assert "JHU Computer Science master's count: 12" in output


@pytest.mark.analysis
def test_question_8():
    cursor = FakeCursor(fetchone_values=[(7,)])

    result = query_data.question_8(cursor)

    assert result == 7


@pytest.mark.analysis
def test_question_9(capsys):
    cursor = FakeCursor(fetchone_values=[(10,)])

    query_data.question_9(cursor, 7)

    output = capsys.readouterr().out

    assert "Original-field count: 7" in output
    assert "LLM-field count: 10" in output
    assert "Difference: +3" in output


@pytest.mark.analysis
def test_question_10(capsys):
    cursor = FakeCursor(
        fetchall_values=[
            ("Johns Hopkins University", 10),
            ("Stanford University", 8),
        ]
    )

    query_data.question_10(cursor)

    output = capsys.readouterr().out

    assert "Top 5 universities by application count:" in output
    assert "Johns Hopkins University: 10" in output
    assert "Stanford University: 8" in output


@pytest.mark.analysis
def test_question_11(capsys):
    cursor = FakeCursor(fetchone_values=[(3.82,)])

    query_data.question_11(cursor)

    output = capsys.readouterr().out
    assert "Average GPA of Johns Hopkins University applicants: 3.82" in output

@pytest.mark.db
def test_get_applicant_summary_returns_dict():
    cursor = FakeCursor([(123, "Computer Science", "Accepted", "Fall 2026", 3.85)])

    result = query_data.get_applicant_summary(cursor)

    assert result == {
        "p_id": 123,
        "program": "Computer Science",
        "status": "Accepted",
        "term": "Fall 2026",
        "gpa": 3.85,
    }


@pytest.mark.db
def test_get_applicant_summary_no_row():
    cursor = FakeCursor([None])

    result = query_data.get_applicant_summary(cursor)

    assert result == {}

@pytest.mark.db
def test_main_handles_exception(monkeypatch, capsys):
    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def close(self):
            pass

    monkeypatch.setattr(
        query_data,
        "get_connection",
        lambda: FakeConnection()
    )

    def fake_question_1(cursor):
        raise Exception("test error")

    monkeypatch.setattr(
        query_data,
        "question_1",
        fake_question_1
    )

    query_data.main()

    output = capsys.readouterr().out
    assert "Error running queries: test error" in output

@pytest.mark.db
def test_main_success(monkeypatch):
    class FakeCursorContext:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    class FakeConnection:
        def cursor(self):
            return FakeCursorContext()

        def close(self):
            pass

    monkeypatch.setattr(
        query_data,
        "get_connection",
        lambda: FakeConnection()
    )

    monkeypatch.setattr(query_data, "question_1", lambda cursor: None)
    monkeypatch.setattr(query_data, "question_2", lambda cursor: None)
    monkeypatch.setattr(query_data, "question_3", lambda cursor: None)
    monkeypatch.setattr(query_data, "question_4", lambda cursor: None)
    monkeypatch.setattr(query_data, "question_5", lambda cursor: None)
    monkeypatch.setattr(query_data, "question_6", lambda cursor: None)
    monkeypatch.setattr(query_data, "question_7", lambda cursor: None)
    monkeypatch.setattr(query_data, "question_8", lambda cursor: 5)
    monkeypatch.setattr(query_data, "question_9", lambda cursor, original_count: None)
    monkeypatch.setattr(query_data, "question_10", lambda cursor: None)
    monkeypatch.setattr(query_data, "question_11", lambda cursor: None)

    query_data.main()

@pytest.mark.db
def test_get_connection(monkeypatch):
    class FakeConnection:
        pass

    fake_connection = FakeConnection()

    def fake_connect(**kwargs):
        return fake_connection

    monkeypatch.setattr(query_data.psycopg, "connect", fake_connect)

    result = query_data.get_connection()

    assert result is fake_connection