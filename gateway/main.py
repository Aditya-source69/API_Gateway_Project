from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
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

# ── Rate limiter setup ─────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="API Gateway")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-only-for-local-dev-32chars!!")

# ── Service registry ───────────────────────────────────────────
SERVICES = {
    "users":    "http://localhost:3001",
    "orders":   "http://localhost:3002",
    "payments": "http://localhost:3003",
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

# ── Main gateway route ─────────────────────────────────────────
@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("5/minute")
async def gateway(service: str, path: str, request: Request):

    # Start timer to measure response time
    start_time = time.time()
    client_ip  = request.client.host
    method     = request.method
    full_path  = f"/{service}/{path}"

    logger.info(f"Incoming  | {method} {full_path} | IP: {client_ip}")

    # ── Auth check ─────────────────────────────────────────────
    if full_path not in PUBLIC_ROUTES:
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"Rejected  | {method} {full_path} | No token | IP: {client_ip}")
            return JSONResponse(
                status_code=401,
                content={"error": "Missing or invalid Authorization header"}
            )

        token   = auth_header.split(" ")[1]
        payload = verify_token(token)

        if not payload:
            logger.warning(f"Rejected  | {method} {full_path} | Bad token | IP: {client_ip}")
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or expired token"}
            )

        logger.info(f"Authorized| {method} {full_path} | User: {payload.get('username', 'unknown')}")

    # ── Service routing ────────────────────────────────────────
    if service not in SERVICES:
        logger.error(f"Not Found | {method} {full_path} | Unknown service: {service}")
        return JSONResponse(
            status_code=404,
            content={"error": f"Service '{service}' not found"}
        )

    target_url = f"{SERVICES[service]}/{path}"

    # ── Forward request ────────────────────────────────────────
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=dict(request.headers),
            )

        # Calculate how long the request took
        duration = round((time.time() - start_time) * 1000, 2)

        logger.info(
            f"Completed | {method} {full_path} "
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
            f"Failed    | {method} {full_path} "
            f"| Service unreachable: {service} "
            f"| {duration}ms"
        )
        return JSONResponse(
            status_code=503,
            content={"error": f"Service '{service}' is currently unavailable"}
        )

    except Exception as e:
        logger.error(f"Error     | {method} {full_path} | {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal gateway error"}
        )