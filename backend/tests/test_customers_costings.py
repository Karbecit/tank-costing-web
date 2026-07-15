from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_customer_crud():
    r = client.post(
        "/api/customers",
        json={"company_name": "Test Brewery Ltd", "contact_name": "Jane", "email": "j@test.com"},
    )
    assert r.status_code == 201
    cid = r.json()["id"]

    r = client.get(f"/api/customers/{cid}")
    assert r.json()["company_name"] == "Test Brewery Ltd"

    r = client.put(f"/api/customers/{cid}", json={"phone": "0400000000"})
    assert r.json()["phone"] == "0400000000"

    r = client.get("/api/customers", params={"q": "Brewery"})
    assert any(c["id"] == cid for c in r.json())

    r = client.delete(f"/api/customers/{cid}")
    assert r.status_code == 204


def test_costing_save_and_load():
    payload = {
        "version": 1,
        "title": "Test tank",
        "summary": {"diam": 1200, "expan_diam": 0, "expan_height": 0, "gst": 1.1},
        "cones": [],
        "strakes": [],
    }
    r = client.post(
        "/api/costings",
        json={"title": "Test tank", "payload": payload},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Test tank"
    assert data["payload"]["summary"]["diam"] == 1200
    costing_id = data["id"]

    r = client.get(f"/api/costings/{costing_id}")
    assert r.status_code == 200

    payload["summary"]["diam"] = 1500
    r = client.put(
        f"/api/costings/{costing_id}",
        json={"title": "Updated tank", "payload": payload},
    )
    assert r.json()["title"] == "Updated tank"
    assert r.json()["payload"]["summary"]["diam"] == 1500

    r = client.delete(f"/api/costings/{costing_id}")
    assert r.status_code == 204
