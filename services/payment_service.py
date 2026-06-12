from fastapi import FastAPI

app = FastAPI(title="Payment Service")

@app.get("/payments")
def get_payments():
    return {
        "service": "Payment Service",
        "status": "All payments cleared"
    }