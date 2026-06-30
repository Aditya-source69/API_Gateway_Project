from fastapi.testclient import TestClient
from services.auth_service import app
client = TestClient(app)

def test_login_success():
    r = client.post("/auth/login", json={"username": "adi", "password": "password123"})
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_login_wrong_password():
    r = client.post("/auth/login", json={"username": "adi", "password": "WRONG"})
    assert r.status_code == 401