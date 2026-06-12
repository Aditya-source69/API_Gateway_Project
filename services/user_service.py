from fastapi import FastAPI

app = FastAPI(title="User Service")

@app.get("/users")
def get_users():
    return {
        "service": "User Service",
        "users": ["Adi", "Rahul", "Priya"]
    }