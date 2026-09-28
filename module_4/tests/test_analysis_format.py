import os
import sys
import re

import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.mark.analysis
def test_analysis_contains_answer_labels(client):
    response = client.get("/analysis")

    assert response.status_code == 200

    page = response.data.decode("utf-8")

    assert "Answer:" in page


@pytest.mark.analysis
def test_percentage_formatting(client):
    response = client.get("/analysis")

    assert response.status_code == 200

    page = response.data.decode("utf-8")

    percentages = re.findall(r"Answer:\s*(\d+\.\d{2})%", page)

    assert len(percentages) >= 1