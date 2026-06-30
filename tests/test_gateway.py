from fastapi.testclient import TestClient
from gateway.main import app, SECRET_KEY
import jwt
import datetime

client = TestClient(app)

# Helper: mint a token the gateway will accept — signed with the gateway's OWN
# SECRET_KEY, exactly like the auth service does. We need this to test the
# protected routes.
def make_valid_token():
    payload = {
        "username": "adi",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def test_gateway_health_is_public():
    r = client.get("/health")
    assert r.status_code == 200

def test_missing_token_rejected():
    r = client.get("/orders")            # no Authorization header
    assert r.status_code == 401

def test_bad_token_rejected():
    r = client.get("/orders", headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401

def test_unknown_service_returns_404():
    token = make_valid_token()
    r = client.get("/nope", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 404