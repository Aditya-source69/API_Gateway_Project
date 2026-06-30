from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import jwt
import datetime
import os

app = FastAPI(title="Auth Service")

# ── Secret key ──
# Read from the environment so the gateway and this service share the SAME
# key. The default is for local dev only; in Docker/production we inject a
# real secret via an environment variable (12-factor config).
# IMPORTANT: this default MUST match the gateway's default in gateway/main.py.
SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-only-for-local-dev-32chars!!")

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