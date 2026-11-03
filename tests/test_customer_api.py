import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

VALID = {
    "email": "Jane.Doe@Example.com",
    "password": "Str0ngPass",
    "first_name": "Jane",
    "last_name": "Doe",
    "phone": "+1 555-0100",
    "address": "1 Main St",
}


@pytest.fixture()
def client(tmp_path):
    settings = Settings(db_path=str(tmp_path / "test.db"), secret_key="test-secret")
    return TestClient(create_app(settings))


def register(client, **overrides):
    return client.post("/api/customers/register", json={**VALID, **overrides})


def login(client, email=VALID["email"], password=VALID["password"]):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def test_register_success_normalizes_email_and_hides_password(client):
    res = register(client)
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "jane.doe@example.com"
    assert body["first_name"] == "Jane"
    assert "password" not in body and "password_hash" not in body


def test_register_duplicate_email_returns_409(client):
    register(client)
    res = register(client, email="jane.doe@example.com")
    assert res.status_code == 409


@pytest.mark.parametrize("password", ["short1A", "alllowercase1", "ALLUPPERCASE1", "NoDigitsHere"])
def test_register_rejects_weak_password(client, password):
    assert register(client, password=password).status_code == 422


def test_register_rejects_invalid_email_and_phone(client):
    assert register(client, email="not-an-email").status_code == 422
    assert register(client, phone="abc").status_code == 422


def test_login_success_returns_token_and_customer(client):
    register(client)
    res = login(client)
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["customer"]["email"] == "jane.doe@example.com"


def test_login_invalid_credentials_returns_401(client):
    register(client)
    assert login(client, password="WrongPass1").status_code == 401
    assert login(client, email="nobody@example.com").status_code == 401


def test_view_own_details(client):
    customer_id = register(client).json()["id"]
    token = login(client).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/api/customers/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["id"] == customer_id

    by_id = client.get(f"/api/customers/{customer_id}", headers=headers)
    assert by_id.status_code == 200
    assert by_id.json()["last_name"] == "Doe"


def test_view_details_requires_auth(client):
    assert client.get("/api/customers/me").status_code == 401
    assert client.get("/api/customers/me", headers={"Authorization": "Bearer bad.token.value"}).status_code == 401


def test_cannot_view_other_customer(client):
    register(client)
    other_id = register(client, email="other@example.com").json()["id"]
    token = login(client).json()["access_token"]
    res = client.get(f"/api/customers/{other_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
