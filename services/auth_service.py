from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import jwt
import datetime
import os

app = FastAPI(title="Auth Service")

# ── Secret key ──
# Required from the environment — NO hardcoded fallback in the repo. The gateway
# and this service must be given the SAME key (via .env / compose / K8s Secret)
# so tokens signed here verify at the gateway.
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required and is not set.")

# ── Fake user database ──
FAKE_USERS = {
    "adi": "password123",
    "rahul": "pass456"
}

# ── Request body model ──
class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/login")
def login(request: LoginRequest):

    # Check if user exists and password matches
    if request.username not in FAKE_USERS:
        raise HTTPException(status_code=401, detail="User not found")
    
    if FAKE_USERS[request.username] != request.password:
        raise HTTPException(status_code=401, detail="Wrong password")

    # Create JWT token
    payload = {
        "username": request.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return {"access_token": token, "token_type": "bearer"}