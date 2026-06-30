# API Gateway Project — Learning Progress & DevOps Roadmap

> A living document tracking what we're building, why, and where we're headed.
> **Last updated:** June 28, 2026

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
- **YAML from scratch**: key:value (space after colon!), lists, indentation = ownership, spaces never tabs, case-sensitive keys; "valid YAML" vs "valid Kubernetes" are different things
- **Kubernetes core**: cluster/node/pod/Deployment/Service; the 4-key manifest skeleton (apiVersion, kind, metadata, spec); labels + selectors as the glue; Deployments give self-healing/scaling (bare Pods don't); Services give stable DNS in front of changing pods; Secrets for shared config; `kubectl apply/get/logs/delete`, `kubectl explain`, `kubectl port-forward`, `minikube image load`; whole API gateway deployed to minikube and tested end-to-end
- **Kubernetes intermediate**: `/health` endpoints + liveness/readiness probes (liveness=restart, readiness=remove from traffic); rolling updates protect against bad deploys (readiness gates the cutover — lived through a failed deploy and recovered); building images into minikube's own Docker daemon (`minikube docker-env`); Ingress + NGINX Ingress Controller for a real URL (`apigw.local` via `minikube tunnel` + hosts entry); HPA autoscaling on CPU (needs metrics-server + CPU requests), watched it scale gateway 1→2 under load, understands the scale-up-fast/scale-down-slow (anti-flapping) behavior and the replica math

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
| **Phase 2** | **Kubernetes core** (minikube — pods, deployments, services) | ✅ Done |
| **Phase 3** | **Kubernetes intermediate** (Ingress, probes, HPA autoscaling) | ✅ Done |
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

---

## 9. Weekly Build Review Log

### Week ending Sun, June 28, 2026

**What happened this week — a huge build week.** Last week's milestone was modest: one Deployment + one Service reached via `kubectl port-forward`. Adi blew past it and shipped **all of Kubernetes core AND intermediate** in a single week. Concretely:

- A full `k8s/` directory with **9 hand-written manifests**: `gateway.yaml` (Deployment + Service), the 4 backend services, `secret.yaml`, `ingress.yaml`, `hpa.yaml`.
- **Probes on every Deployment** — `/health` endpoints added to the gateway and all 4 services, wired to liveness + readiness probes.
- **Ingress + NGINX Ingress Controller** — a real URL (`apigw.local`) replacing `port-forward`, via `minikube tunnel` + a hosts entry.
- **HorizontalPodAutoscaler** scaling the gateway on CPU (1→2 watched live under load); understands the `ceil(replicas × currentCPU ÷ targetCPU)` math and the scale-up-fast/down-slow anti-flapping behavior.
- **Real debugging under fire**: diagnosed a stale-image bug (pods ran cached `:latest`) and fixed it with `minikube docker-env` → rebuild → `kubectl rollout restart`; and lived through a *failed* rolling deploy where the **readiness probe kept the old pods serving** — saw zero-downtime protection work for real.
- Wrote `PHASE3-NOTES.md` — a genuinely good CKA-style cheat-sheet (concepts, command reference, debugging order, challenges & lessons).

**Honest status:** This is real, well-above-pace progress. Roadmap Phase 2 (K8s core) and Phase 3 (K8s intermediate) are both **Done** — verified against actual manifests and notes, not just claims. He is now ready to start **Phase 4 — CI/CD**.

**Still owed from the daily quizzes (carry-over, not blockers):** JWT **tamper-evidence** (editing `exp` breaks the signature → 401; it *oscillates*, not durably locked) and **Host header value-naming** (say both concrete values aloud). Spot-check these, don't re-teach from scratch.

**Milestone set for next week:** Build his **first CI/CD pipeline** — a GitLab CI `.gitlab-ci.yml` that runs on every push: lint → test → build the Docker image. (Steps in the review message.)

**To measure against next week:** Does a `.gitlab-ci.yml` exist and has a pipeline actually *run green* on GitLab? Can he explain what a runner is, what a stage vs a job is, and why CI builds the image instead of his laptop? Did he add at least one real test that the pipeline executes?

### Week ending Sun, June 21, 2026

**What happened this week:** A strong run of *conceptual* sessions that deliberately bridge toward Kubernetes — but no hands-on K8s build yet. Topics covered: async/concurrency, authn vs authz, HTTP status codes, the Host header & reverse-proxy header rewriting, JWT internals, **networking (ports / localhost / DNS)** as the explicit K8s on-ramp, and rate limiting internals. Two long-standing misconceptions got **locked**: `await` frees the loop (not blocks it), and "every 4xx is the caller's fault, whichever box emits it." `401 vs 403` also locked.

**Honest status:** No `k8s/` manifests, no minikube cluster, no `kubectl` commands run yet. The roadmap doc previously implied Phase 2 was underway; in reality the groundwork (networking/DNS mental model) is laid and the hands-on part is the next step. That's exactly where a self-taught learner *should* be before writing first YAML — but the building hasn't started.

**Milestone set for next week:** Deploy the existing gateway image to a local minikube cluster — one Deployment + one Service, reachable via `kubectl port-forward`. (Steps in the review message.)

**To measure against next week:** Does `kubectl get pods` show a Running gateway pod? Can he reach `/` (or a service) through the Service? Can he explain Pod vs Deployment vs Service in his own words, and debug one CrashLoopBackOff?

