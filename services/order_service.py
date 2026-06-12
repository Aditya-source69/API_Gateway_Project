from fastapi import FastAPI

app = FastAPI(title="Order Service")

@app.get("/orders")
def get_orders():
    return {
        "service": "Order Service",
        "orders": ["Order#1", "Order#2", "Order#3"]
    }