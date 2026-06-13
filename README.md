# API Gateway Project

A learning project implementing an **API Gateway pattern** in Python using FastAPI. The gateway acts as a single entry point that handles authentication, rate limiting, and request routing to backend microservices.

> Built with Python 3.10, FastAPI, and JWT authentication.

---

## What We Built

### Architecture

```
Client
  │
  ▼
┌──────────────────────────────┐
│         API Gateway          │  ← main.py (port 8000)
│                              │
│  1. Rate Limiting (5 req/min)│
│  2. JWT Auth Check           │
│  3. Service Lookup           │
│  4. Request Forwarding       │
│  5. Structured Logging       │
└──────────────────────────────┘
         │          │          │
         ▼          ▼          ▼
    User Service  Order     Payment
    :3001         Service   Service
                  :3002     :3003

Auth Service runs separately at :8001
```

### Files

| File | What it does |
|------|--------------|
| `gateway/main.py` | Core API Gateway — rate limiting, JWT verification, routing, logging |
| `services/auth_service.py` | Auth microservice — login endpoint that issues JWT tokens |
| `services/user_service.py` | User microservice — returns a list of users |
| `services/order_service.py` | Order microservice — returns a list of orders |
| `services/payment_service.py` | Payment microservice — returns payment status |
| `gateway/gateway.log` | Auto-generated request/response audit log |

---

## Key Concepts Covered

### 1. API Gateway Pattern
A single reverse proxy that all clients talk to. The gateway handles cross-cutting concerns (auth, rate limiting, logging) so individual microservices don't have to.

### 2. JWT Authentication
- Client POSTs credentials to `/auth/login` → receives a JWT token
- Every subsequent request includes `Authorization: Bearer <token>`
- Gateway verifies the token signature and expiry before forwarding
- Only `/auth/login` is a public route; all others are protected

### 3. Rate Limiting
Uses `slowapi` to cap requests at **5 per minute per IP address**. Exceeding this returns HTTP 429.

### 4. Request Forwarding
Uses `httpx` (async HTTP client) to proxy the request to the correct microservice, preserving headers and method.

### 5. Service Registry
A simple Python dict maps service names to their base URLs:
```python
SERVICES = {
    "users":    "http://localhost:3001",
    "orders":   "http://localhost:3002",
    "payments": "http://localhost:3003",
}
```
The route pattern `/{service}/{path}` extracts the service name and looks it up here.

### 6. Structured Logging
Every request is logged with: timestamp, event type, method, path, IP, username (if authenticated), response status, and duration in ms.

```
2026-06-09 | INFO | Incoming  | GET /users/list | IP: 127.0.0.1
2026-06-09 | INFO | Authorized| GET /users/list | User: adi
2026-06-09 | INFO | Completed | GET /users/list | Status: 200 | 12.4ms
```

---

## Running the Project

### Prerequisites
```bash
cd api-gateway-project
python -m venv venv
venv\Scripts\activate          # Windows
pip install fastapi uvicorn httpx pyjwt slowapi
```

### Start each service in a separate terminal

```bash
# Terminal 1 — API Gateway
uvicorn gateway.main:app --port 8000 --reload

# Terminal 2 — Auth Service
uvicorn services.auth_service:app --port 8001 --reload

# Terminal 3 — User Service
uvicorn services.user_service:app --port 3001 --reload

# Terminal 4 — Order Service
uvicorn services.order_service:app --port 3002 --reload

# Terminal 5 — Payment Service
uvicorn services.payment_service:app --port 3003 --reload
```

### Test it

**Step 1 — Get a token:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "adi", "password": "password123"}'
```

**Step 2 — Call a protected service:**
```bash
curl http://localhost:8000/users \
  -H "Authorization: Bearer <token_from_step_1>"
```

**Test credentials:** `adi / password123` or `rahul / pass456`

---

## Error Responses

| Status | Meaning |
|--------|---------|
| 401 | Missing, expired, or invalid JWT token |
| 404 | Service name not in the registry |
| 429 | Rate limit exceeded (5 req/min) |
| 503 | Target microservice is down/unreachable |
| 500 | Unexpected gateway error |

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| FastAPI | Web framework for gateway and services |
| Uvicorn | ASGI server |
| httpx | Async HTTP client for forwarding requests |
| PyJWT | JWT encoding/decoding |
| slowapi | Rate limiting middleware |
| Pydantic | Request body validation |

---

## What's Intentionally Simplified (for learning)

- **Fake user DB** — hardcoded dict in auth_service.py; real apps use a database with hashed passwords
- **Hardcoded SECRET_KEY** in auth_service.py — real apps load from environment variables
- **Hardcoded service URLs** — real systems use service discovery (Consul, Kubernetes DNS, etc.)
- **No request body forwarding** — the gateway currently doesn't stream the request body to downstream services
- **Single gateway instance** — production would run multiple instances behind a load balancer
