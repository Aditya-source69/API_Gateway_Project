from fastapi import FastAPI

app = FastAPI(title="User Service")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/users")
def get_users():
    return {
        "service": "User Service",
        "users": ["Adi", "Rahul", "Priya"]
    }
