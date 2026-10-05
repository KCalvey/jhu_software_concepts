import os
import sys

import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as client:
        yield client


@pytest.mark.buttons
def test_update_analysis_not_busy(client, monkeypatch):
    monkeypatch.setattr(app_module, "SCRAPE_PROCESS", None)

    response = client.post("/update-analysis")

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}


@pytest.mark.buttons
def test_update_analysis_busy(client, monkeypatch):
    class FakeProcess:
        def poll(self):
            return None

    monkeypatch.setattr(app_module, "SCRAPE_PROCESS", FakeProcess())

    response = client.post("/update-analysis")

    assert response.status_code == 409
    assert response.get_json() == {"busy": True}


@pytest.mark.buttons
def test_pull_data_busy(client, monkeypatch):
    class FakeProcess:
        def poll(self):
            return None

    monkeypatch.setattr(app_module, "SCRAPE_PROCESS", FakeProcess())

    response = client.post("/pull-data")

    assert response.status_code == 409
    assert response.get_json() == {"busy": True}


@pytest.mark.buttons
def test_pull_data_starts_process(client, monkeypatch):
    class FakeProcess:
        def poll(self):
            return None

    def fake_popen(command):
        return FakeProcess()

    monkeypatch.setattr(app_module, "SCRAPE_PROCESS", None)
    monkeypatch.setattr(app_module.subprocess, "Popen", fake_popen)

    response = client.post("/pull-data")

    assert response.status_code == 202
    assert response.get_json() == {"ok": True}
    assert app_module.SCRAPE_PROCESS is not None