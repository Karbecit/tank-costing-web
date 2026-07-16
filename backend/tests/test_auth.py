from fastapi.testclient import TestClient

from app.database import init_db
from app.main import app


def test_login_and_me(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == "admin@test.local"
    assert r.json()["role"] == "admin"


def test_login_invalid():
    init_db()
    c = TestClient(app)
    r = c.post("/api/auth/login", json={"email": "admin@test.local", "password": "wrong"})
    assert r.status_code == 401


def test_protected_route_requires_auth():
    init_db()
    c = TestClient(app)
    r = c.get("/api/customers")
    assert r.status_code == 401


def test_admin_create_user(client):
    r = client.post(
        "/api/admin/users",
        json={
            "email": "editor@test.local",
            "display_name": "Editor",
            "password": "EditorPass1",
            "role": "editor",
        },
    )
    assert r.status_code == 201
    assert r.json()["role"] == "editor"
