from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import jwt
import datetime

app = FastAPI(title="Auth Service")

# ── Secret key (in real apps, store this in environment variables) ──
SECRET_KEY = "your-super-secret-key"

# ── Fake user database ──
FAKE_USERS = {
    "adi": "password123",
    "rahul": "pass456"
}

# ── Request body model ──
class LoginRequest(BaseModel):
    username: str
    password: str

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