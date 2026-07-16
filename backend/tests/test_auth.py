import pyotp
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


def test_change_password(client):
    r = client.post(
        "/api/auth/change-password",
        json={"current_password": "TestAdmin123!", "new_password": "NewAdmin123!"},
    )
    assert r.status_code == 204
    r = client.post(
        "/api/auth/login",
        json={"email": "admin@test.local", "password": "NewAdmin123!"},
    )
    assert r.status_code == 200
    client.post(
        "/api/auth/change-password",
        json={"current_password": "NewAdmin123!", "new_password": "TestAdmin123!"},
    )


def test_mfa_login_flow(client):
    setup = client.post("/api/auth/mfa/setup")
    assert setup.status_code == 200
    secret = setup.json()["secret"]
    code = pyotp.TOTP(secret).now()
    assert client.post("/api/auth/mfa/confirm", json={"code": code}).status_code == 204

    login = client.post(
        "/api/auth/login",
        json={"email": "admin@test.local", "password": "TestAdmin123!"},
    )
    assert login.status_code == 200
    assert login.json().get("mfa_required") is True
    mfa_token = login.json()["mfa_token"]
    code = pyotp.TOTP(secret).now()
    verify = client.post(
        "/api/auth/mfa/verify",
        json={"mfa_token": mfa_token, "code": code, "trust_device": False},
    )
    assert verify.status_code == 200
    assert "access_token" in verify.json()

    disable_code = pyotp.TOTP(secret).now()
    client.post("/api/auth/mfa/disable", json={"code": disable_code})


def test_admin_audit_log(client):
    r = client.get("/api/admin/audit")
    assert r.status_code == 200
    entries = r.json()
    assert isinstance(entries, list)
    assert any(e["action"] == "user.create" for e in entries)
