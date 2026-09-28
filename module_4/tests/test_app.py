import os
import sys
from urllib import response

import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")),
)

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

@pytest.mark.buttons

def test_update_analysis_not_busy(client):
    response = client.post("/update-analysis")

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}

@pytest.mark.buttons

def test_update_analysis_busy(client, monkeypatch):
    import app as app_module

    class FakeProcess:
        def poll(self):
            return None

    monkeypatch.setattr(app_module, "scrape_process", FakeProcess())

    response = client.post("/update-analysis")

    assert response.status_code == 409
    assert response.get_json() == {"busy": True}

@pytest.mark.web

def test_analysis_page_loads(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Grad School Cafe Data Analysis" in response.data