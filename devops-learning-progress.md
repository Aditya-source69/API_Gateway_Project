# API Gateway Project — Learning Progress & DevOps Roadmap

> A living document tracking what we're building, why, and where we're headed.
> **Last updated:** June 14, 2026

---

## 1. What We're Building Right Now

We're building an **API Gateway from scratch** using **Python + FastAPI**, to learn — hands-on — *why* gateways exist and *how* they actually work under the hood.

### The core idea

Instead of clients talking to many backend services directly, everything goes through **one single entry point** (the gateway). The gateway then handles routing, security, traffic control, and logging on behalf of all the services behind it.

```
                    ┌──────────────────────────┐
 Client ──────────▶ │       API Gateway         │  :8000
                    │   (single entry point)    │
                    └────┬────────┬────────┬────┘
                         │        │        │
                  ┌──────▼─┐ ┌────▼───┐ ┌──▼──────┐
                  │ Users  │ │ Orders │ │Payments │
                  │ :3001  │ │ :3002  │ │  :3003  │
                  └────────┘ └────────┘ └─────────┘

                  ┌──────────────┐
                  │ Auth Service │  :3004  (issues JWT tokens)
                  └──────────────┘
```

### What the gateway does for us today

| Responsibility | What it means |
|---|---|
| **Routing** | `/users` → User Service, `/orders` → Order Service, etc. |
| **Authentication** | Rejects any request without a valid JWT token |
| **Rate limiting** | Blocks clients that send too many requests (5/min per IP) |
| **Logging** | Records every request — method, path, status, time, IP |
| **Error handling** | Returns clean errors when a service is down |

---

## 2. The Tech Stack

| Tool | Role |
|---|---|
| **FastAPI** | The web framework for the gateway + services |
| **Uvicorn** | The server that runs FastAPI apps |
| **httpx** | Async HTTP client — lets the gateway forward requests |
| **PyJWT** | Creates and verifies JWT tokens |
| **slowapi** | Rate limiting per IP address |
| **Python `logging`** | Structured request logs (terminal + `gateway.log`) |
| **Postman** | Testing requests with custom headers and tokens |

---

## 3. Project Structure

```
api-gateway-project/
│
├── services/
│   ├── user_service.py      # :3001
│   ├── order_service.py     # :3002
│   ├── payment_service.py   # :3003
│   └── auth_service.py      # :3004  (login → returns JWT)
│
├── gateway/
│   ├── main.py              # :8000  (the gateway itself)
│   └── gateway.log          # request logs saved here
│
└── venv/                    # virtual environment
```

---

## 4. Progress So Far — API Gateway Project

| Phase | Topic | Status |
|---|---|---|
| **Phase 1** | Setup & 3 microservices (FastAPI) | ✅ Done |
| **Phase 2** | Gateway routing + reverse proxy | ✅ Done |
| **Phase 3** | Authentication with JWT tokens | ✅ Done |
| **Phase 4** | Rate limiting (slowapi) | ✅ Done |
| **Phase 5** | Logging & error handling | ✅ Done |
| **Phase 6** | Dockerizing the whole system | ✅ Done |

**Gateway build complete.** All phases working: routing, auth, rate limiting, logging, error handling — and the whole system now runs in Docker with one command (`docker compose up --build`).

### Key concepts already learned

- What an API gateway is and the problem it solves
- How a reverse proxy forwards requests between services
- How JWT authentication works (header → payload → signature)
- How a token flows: login → receive token → send in `Authorization: Bearer` header → gateway verifies
- Why rate limiting matters and how per-IP limits work
- Why structured logging is essential for real systems
- Windows PowerShell quirks (`New-Item` instead of `touch`, one `mkdir` per command, venv activation, quoting paths with spaces)
- **Docker**: images vs containers, the Dockerfile, layer caching (copy requirements first), `--host 0.0.0.0` inside containers, `.dockerignore`
- **Docker Compose**: one command for the whole system, service-name DNS (containers reach each other by name, not `localhost`), exposing only the gateway port, injecting secrets/config via environment variables (12-factor config)

---

## 5. What's Next in This Project

### Phase 5 (finishing now) — Logging & Error Handling
- Log every request with timestamp, status, and response time
- Save logs to `gateway.log`
- Gracefully handle a service being down (return `503` instead of crashing)

### Phase 6 — Docker
- Package each service + the gateway into containers
- Use **Docker Compose** to run everything with a single command instead of 5 terminals
- This is the bridge into the larger DevOps roadmap below

---

## 6. The Bigger Picture — DevOps Roadmap

This gateway project is the foundation. Here's the full 6-phase DevOps journey it feeds into:

| Phase | Focus | Status |
|---|---|---|
| **Phase 1** | **Docker** — containerize the FastAPI services | ✅ Done |
| **Phase 2** | **Kubernetes core** (minikube — pods, deployments, services) | ⬜ Not started |
| **Phase 3** | **Kubernetes intermediate** (Ingress, probes, HPA autoscaling) | ⬜ Not started |
| **Phase 4** | **CI/CD** with GitLab CI (build → test → deploy pipelines) | ⬜ Not started |
| **Phase 5** | **Terraform + AWS** (infrastructure as code) | ⬜ Not started |
| **Phase 6** | **Observability** (Prometheus + Grafana) + CKA exam prep | ⬜ Not started |

### How the gateway project connects to each phase

- **Docker** → containerize the 5 services we just built
- **Kubernetes** → run those containers at scale, with self-healing and load balancing
- **CI/CD** → automatically test and deploy the gateway on every code change
- **Terraform/AWS** → provision the cloud infrastructure it all runs on
- **Observability** → the logging we added in Phase 5 grows into full monitoring dashboards

---

## 7. Quick Reference — Running the System

Open **5 terminals**, activate the venv in each (`venv\Scripts\activate`), then:

```powershell
# Terminal 1 — User Service
uvicorn services.user_service:app --port 3001

# Terminal 2 — Order Service
uvicorn services.order_service:app --port 3002

# Terminal 3 — Payment Service
uvicorn services.payment_service:app --port 3003

# Terminal 4 — Auth Service
uvicorn services.auth_service:app --port 3004

# Terminal 5 — Gateway
uvicorn gateway.main:app --port 8000 --reload
```

### Testing flow (Postman)

```
1. POST http://localhost:3004/auth/login
   Body (JSON): { "username": "adi", "password": "password123" }
   → returns access_token

2. GET http://localhost:8000/users
   Header: Authorization = Bearer <access_token>
   → returns the users list
```

---

## 8. Milestones Hit 🎉

- ✅ Built 4 working FastAPI services from zero
- ✅ Built a functioning API gateway that routes traffic
- ✅ Secured it with real JWT authentication
- ✅ Added production-style rate limiting
- 🔄 Adding logging & graceful error handling
- ⬜ Next big step: Docker

*Not bad at all for someone who hadn't touched FastAPI before starting this.*
