from pathlib import Path

import pytest

from app.services.jma_service import jma_file_to_payload
from app.services.pdf_service import generate_quote_pdf

LEGACY_JMA = (
    Path(__file__).resolve().parents[3]
    / "Old Program"
    / "Code"
    / "Costings"
    / "Sheet19.jma"
)
LADBROKE_JMA = (
    Path(__file__).resolve().parents[3]
    / "Ladbroke Grove Wines 35kl storage tank 3050diam 4800wall 316 stst 14-7-09.jma"
)


def _sample_payload():
    return {
        "version": 1,
        "cones_rate_per_hour": 55,
        "summary": {
            "diam": 1200,
            "expan_diam": 450,
            "expan_height": 100,
            "coil_mark_up_percent": 25,
            "gst": 1.1,
            "num_tanks": 1,
        },
        "cones": [
            {
                "name": "Top",
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
            }
        ]
        + [{}] * 4,
        "strakes": [{"used": 1, "thick": 2, "width": 1500, "price_kg": 5.8}] + [{}] * 7,
    }


@pytest.mark.skipif(not LADBROKE_JMA.exists(), reason="Ladbroke Grove QA .jma not available")
def test_ladbroke_jma_import_payload():
    payload = jma_file_to_payload(LADBROKE_JMA)
    assert payload["company_name"] == "Ladbroke Grove Wines"
    assert payload["summary"]["diam"] == 3050
    assert payload["summary"]["num_tanks"] == 6
    assert payload["summary"]["price_quoted"] == 18850
    assert payload["summary"]["components_price"] == 2654
    assert payload["cones"][0]["offset_select"]
    assert payload["cones"][3]["slope_select"]


@pytest.mark.skipif(not LADBROKE_JMA.exists(), reason="Ladbroke Grove QA .jma not available")
def test_ladbroke_jma_calculate_totals():
    from app.calc.costing import calculate_costing
    from app.jma.reader import load_jma_full
    from tests.test_strakes_summary import _input_cone, _input_strake

    cones, strakes, summary, stored = load_jma_full(LADBROKE_JMA)
    result = calculate_costing(
        [_input_cone(c) for c in cones],
        [_input_strake(s) for s in strakes],
        summary,
    )
    t = result.totals
    assert t.total_vol == pytest.approx(stored.total_vol, rel=1e-3)
    assert t.steel_total == pytest.approx(stored.steel_total, rel=1e-3)
    assert t.single_tank_less_gst == pytest.approx(21829.02, rel=1e-3)


@pytest.mark.skipif(not LEGACY_JMA.exists(), reason="Legacy .jma sample not available")
def test_jma_import_payload():
    payload = jma_file_to_payload(LEGACY_JMA)
    assert payload["title"]
    assert len(payload["cones"]) == 5
    assert len(payload["strakes"]) == 8
    assert payload["summary"]["diam"] > 0


@pytest.mark.skipif(not LEGACY_JMA.exists(), reason="Legacy .jma sample not available")
def test_jma_import_api(client):
    with LEGACY_JMA.open("rb") as handle:
        r = client.post(
            "/api/jma/import",
            files={"file": ("Sheet19.jma", handle, "application/octet-stream")},
        )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["id"]
    assert data["payload"]["cones"]


def test_smtp_settings_admin(client):
    r = client.get("/api/admin/settings/smtp")
    assert r.status_code == 200
    assert "smtp_host" in r.json()

    r = client.put(
        "/api/admin/settings/smtp",
        json={
            "smtp_host": "smtp.test.local",
            "smtp_port": 587,
            "smtp_user": "user",
            "smtp_from": "test@test.local",
            "smtp_use_tls": True,
            "app_base_url": "http://localhost:5173",
        },
    )
    assert r.status_code == 200
    assert r.json()["configured"] is True


def test_quote_pdf(client):
    create = client.post(
        "/api/costings",
        json={"title": "PDF Test Tank", "quote_ref": "Q-TEST", "payload": _sample_payload()},
    )
    assert create.status_code == 201
    cid = create.json()["id"]
    r = client.get(f"/api/costings/{cid}/quote.pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"


def test_pdf_service_bytes():
    pdf = generate_quote_pdf(title="Test", quote_ref="Q1", payload=_sample_payload())
    assert pdf[:4] == b"%PDF"


@pytest.mark.skipif(not LEGACY_JMA.exists(), reason="Legacy .jma sample not available")
def test_jma_export_roundtrip():
    from app.jma.reader import _read_tokens
    from app.jma.writer import build_jma_tokens

    payload = jma_file_to_payload(LEGACY_JMA)
    tokens = build_jma_tokens(
        payload,
        title=payload["title"],
        quote_ref=payload.get("quote_ref"),
        company_name=payload.get("company_name") or "",
    )
    assert len(tokens) >= 1400
    orig = _read_tokens(LEGACY_JMA)
    summary_start = 392
    assert abs(float(orig[summary_start + 20]) - float(tokens[summary_start + 20])) < 1


def test_dip_chart_api(client):
    r = client.post(
        "/api/calc/dip-chart",
        json={"payload": _sample_payload(), "increment_mm": 10},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["rows"]
    assert data["total_volume_litres"] > 0


def test_jma_export_api(client):
    create = client.post(
        "/api/costings",
        json={"title": "Export test", "payload": _sample_payload()},
    )
    assert create.status_code == 201
    cid = create.json()["id"]
    r = client.get(f"/api/costings/{cid}/export.jma")
    assert r.status_code == 200
    assert len(r.content) > 1000
