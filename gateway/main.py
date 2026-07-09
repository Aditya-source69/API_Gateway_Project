from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
import httpx
import jwt
import logging
import os
import time

# ── Logging setup ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),                  # Print to terminal
        logging.FileHandler("gateway/gateway.log") # Save to file
    ]
)
logger = logging.getLogger("api-gateway")

# ── Lifespan: create ONE shared HTTP client for the gateway's whole life ──
# Runs once on startup, and once on shutdown. The single AsyncClient holds a
# connection pool that is reused across every forwarded request, so we no
# longer pay the TCP/TLS handshake cost on each call.
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient()   # ← created once, at startup
    yield                                          # ← gateway runs here
    await app.state.http_client.aclose()           # ← closed once, at shutdown

# ── Rate limiter setup ─────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="API Gateway", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Require the secret from the environment — NO hardcoded fallback in the repo.
# Provided locally via .env, in Docker via compose env, in K8s via a Secret.
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required and is not set.")

# ── Service registry ───────────────────────────────────────────
# Maps the first path segment to a backend base URL.
# "auth" is included so login can flow THROUGH the gateway like everything else.
#
# URLs come from environment variables so the SAME code works in two worlds:
#   • Running locally (5 terminals): defaults to http://localhost:<port>
#   • Running in Docker Compose: env overrides to http://<service-name>:<port>
#     (Compose gives every container a DNS name equal to its service name)
SERVICES = {
    "users":    os.environ.get("USER_SERVICE_URL",    "http://localhost:3001"),
    "orders":   os.environ.get("ORDER_SERVICE_URL",   "http://localhost:3002"),
    "payments": os.environ.get("PAYMENT_SERVICE_URL", "http://localhost:3003"),
    "auth":     os.environ.get("AUTH_SERVICE_URL",    "http://localhost:3004"),
}

PUBLIC_ROUTES = ["/auth/login"]

# ── Token verification ─────────────────────────────────────────
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
@app.get("/health")
def health():
    return {"status": "ok"}

# ── Main gateway route ─────────────────────────────────────────
# Catch-all: capture the ENTIRE path, then split off the first segment
# as the service name. This lets us forward the original path untouched.
@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("5/minute")
async def gateway(full_path: str, request: Request):

    # Start timer to measure response time
    start_time = time.time()
    client_ip  = request.client.host
    method     = request.method
    path       = f"/{full_path}"          # original path, e.g. /users or /auth/login

    logger.info(f"Incoming  | {method} {path} | IP: {client_ip}")

    # ── Auth check ─────────────────────────────────────────────
    if path not in PUBLIC_ROUTES:
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"Rejected  | {method} {path} | No token | IP: {client_ip}")
            return JSONResponse(
                status_code=401,
                content={"error": "Missing or invalid Authorization header"}
            )

        token   = auth_header.split(" ")[1]
        payload = verify_token(token)

        if not payload:
            logger.warning(f"Rejected  | {method} {path} | Bad token | IP: {client_ip}")
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or expired token"}
            )

        logger.info(f"Authorized| {method} {path} | User: {payload.get('username', 'unknown')}")

    # ── Service routing ────────────────────────────────────────
    # The service name is the FIRST segment of the path (/users/... -> "users").
    service = full_path.split("/")[0]

    if service not in SERVICES:
        logger.error(f"Not Found | {method} {path} | Unknown service: {service}")
        return JSONResponse(
            status_code=404,
            content={"error": f"Service '{service}' not found"}
        )

    # Forward the FULL original path to the backend (don't strip the prefix).
    target_url = f"{SERVICES[service]}{path}"

    # ── Forward request ────────────────────────────────────────
    try:
        # Read the incoming body so we can forward it (needed for POST/PUT).
        body = await request.body()

        # Drop the Host header: it still points at the gateway, which can
        # confuse the backend. Let httpx set the correct one.
        fwd_headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}

        # Reuse the ONE client created at startup (see lifespan above).
        # No `async with` here — we do NOT want to open/close a client per request.
        client = request.app.state.http_client
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=fwd_headers,
            content=body,
        )

        # Calculate how long the request took
        duration = round((time.time() - start_time) * 1000, 2)

        logger.info(
            f"Completed | {method} {path} "
            f"| Status: {response.status_code} "
            f"| {duration}ms"
        )

        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )

    # ── Error handling — what if a service is down? ────────────
    except httpx.ConnectError:
        duration = round((time.time() - start_time) * 1000, 2)
        logger.error(
            f"Failed    | {method} {path} "
            f"| Service unreachable: {service} "
            f"| {duration}ms"
        )
        return JSONResponse(
            status_code=503,
            content={"error": f"Service '{service}' is currently unavailable"}
        )

    except Exception as e:
        logger.error(f"Error     | {method} {path} | {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal gateway error"}
        )