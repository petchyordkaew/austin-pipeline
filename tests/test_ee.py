"""
Automated tests. GitHub Actions runs these on every push (see .github/workflows/ci.yml).
If any test fails, the pipeline stops and nothing broken gets built or deployed.
That's the "CI" part: Continuous Integration = every change is checked automatically.

Run locally with:  pytest
"""

import pytest
from fastapi.testclient import TestClient

from app import ee
from app.main import app

client = TestClient(app)


def test_4_band_resistor():
    result = ee.resistor_from_bands(["yellow", "violet", "red", "gold"])
    assert result["ohms"] == 4700
    assert result["pretty"] == "4.7 kΩ"
    assert result["tolerance_percent"] == 5


def test_5_band_resistor():
    # brown black black red brown = 100 * 100 = 10 kΩ ±1%
    result = ee.resistor_from_bands(["brown", "black", "black", "red", "brown"])
    assert result["ohms"] == 10_000


def test_gold_multiplier():
    # red red gold gold = 22 * 0.1 = 2.2 Ω
    assert ee.resistor_from_bands(["red", "red", "gold", "gold"])["ohms"] == 2.2


def test_bad_color():
    with pytest.raises(ValueError):
        ee.resistor_from_bands(["pink", "black", "red", "gold"])


def test_ohms_law():
    assert ee.ohms_law(v=12, r=4)["i"] == 3


def test_voltage_divider():
    assert ee.voltage_divider(10, 1000, 1000)["vout"] == 5


def test_api_endpoint():
    # Tests the web layer end to end, without starting a real server.
    response = client.get("/resistor", params={"bands": "brown,black,orange,gold"})
    assert response.status_code == 200
    assert response.json()["ohms"] == 10_000


def test_api_bad_input_returns_400():
    response = client.get("/resistor", params={"bands": "red,red"})
    assert response.status_code == 400


def test_home_page_is_served():
    # The front-end page should load, and it should still say who made it.
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Petch" in response.text


def test_info_endpoint():
    assert client.get("/api/info").json()["version"] == "dev"
