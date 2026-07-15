"""API tests for cone calculation endpoint."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_calc_cone_pettavel_top():
    response = client.post(
        "/api/calc/cone",
        json={
            "cone": {
                "conic_select": 1,
                "angle_select": True,
                "diam_large": 1200,
                "diam_small": 450,
                "angle": 10,
                "knuckle_rad": 30,
                "waste": 300,
                "thick": 2,
                "width": 1500,
                "weight_cucm": 8166,
                "price_kg": 5.8,
            },
            "tank_diam": 1200,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["cone_stat"] == 1  # CONIC_SEL
    assert data["height"] == pytest.approx(91.296, rel=1e-3)
    assert data["volume"] == pytest.approx(65.091, rel=1e-3)
