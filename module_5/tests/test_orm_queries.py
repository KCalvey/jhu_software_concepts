import os
import sys

import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

import orm_queries


class FakeSession:
    def __init__(self, values):
        self.values = list(values)

    def scalar(self, statement):
        return self.values.pop(0)


@pytest.mark.db
def test_question_1(capsys):
    session = FakeSession([25])

    orm_queries.question_1(session)

    output = capsys.readouterr().out
    assert "Fall 2026 applicant count: 25" in output


@pytest.mark.db
def test_question_4(capsys):
    session = FakeSession([3.75])

    orm_queries.question_4(session)

    output = capsys.readouterr().out
    assert "Average GPA American Fall 2026: 3.75" in output


@pytest.mark.db
def test_question_5(capsys):
    session = FakeSession([100, 40])

    orm_queries.question_5(session)

    output = capsys.readouterr().out
    assert "Fall 2025 acceptance percentage: 40.00%" in output


@pytest.mark.db
def test_question_8(capsys):
    session = FakeSession([7])

    result = orm_queries.question_8(session)

    output = capsys.readouterr().out
    assert result == 7
    assert "Original-field count: 7" in output


@pytest.mark.db
def test_question_9(capsys):
    session = FakeSession([10])

    orm_queries.question_9(session, 7)

    output = capsys.readouterr().out
    assert "LLM-field count: 10" in output
    assert "Difference: +3" in output


@pytest.mark.db
def test_question_11(capsys):
    session = FakeSession([3.82])

    orm_queries.question_11(session)

    output = capsys.readouterr().out
    assert "Average GPA of Johns Hopkins University applicants: 3.82" in output

@pytest.mark.db
def test_main(monkeypatch):
    fake_session = FakeSession([25, 3.75, 100, 40, 7, 10, 3.82])

    class FakeSessionContext:
        def __enter__(self):
            return fake_session

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(orm_queries, "Session", FakeSessionContext)

    orm_queries.main()