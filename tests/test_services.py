"""
Tests for the three backend microservices (user, order, payment).

TestClient runs each FastAPI app IN-PROCESS — it sends real requests straight
into the app object and returns the response, with no server or network. Fast,
deterministic, and ideal for CI.
"""
from fastapi.testclient import TestClient

from services.user_service import app as user_app
from services.order_service import app as order_app
from services.payment_service import app as payment_app

# One client per app. Reused across the tests below.
user_client = TestClient(user_app)
order_client = TestClient(order_app)
payment_client = TestClient(payment_app)


# pytest discovers any function named test_*. Inside, we make a request and
# `assert` what we expect. A failed assert = a failed test.

def test_user_health():
    r = user_client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_user_list_returns_users():
    r = user_client.get("/users")
    assert r.status_code == 200
    assert "Adi" in r.json()["users"]

def test_order_health():
    r = order_client.get("/health")
    assert r.status_code == 200

def test_orders_list_has_three():
    r = order_client.get("/orders")
    assert r.status_code == 200
    assert len(r.json()["orders"]) == 3

def test_payment_health():
    r = payment_client.get("/health")
    assert r.status_code == 200

def test_payments_status_cleared():
    r = payment_client.get("/payments")
    assert r.status_code == 200
    assert r.json()["status"] == "All payments cleared"
