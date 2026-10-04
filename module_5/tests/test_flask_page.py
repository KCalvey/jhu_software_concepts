import os
import sys

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


@pytest.mark.web
def test_analysis_page_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Analysis" in response.data
    assert b"Pull Data" in response.data
    assert b"Update Analysis" in response.data
    assert b"Answer:" in response.data