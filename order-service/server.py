from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
app = FastAPI()

# In-memory storage for orders
orders = {}

# Pydantic model for order
class Item(BaseModel):
    name: str
    cost: int

class Order(BaseModel):
    name: str
    cost: int
    items: List[Item]

# Create a new order
@app.post("/orders/", response_model=Order)
def create_order(order: Order):
    order_id = len(orders) + 1
    orders[order_id] = order
    return {"order_id": order_id, **order.dict()}

# Retrieve all orders
@app.get("/orders/", response_model=Dict[int, Order])
def read_orders():
    return orders

# Retrieve a specific order by ID
@app.get("/orders/{order_id}", response_model=Order)
def read_order(order_id: int):
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    return order

# Update a order by ID
@app.put("/orders/{order_id}", response_model=Order)
def update_order(order_id: int, updated_order: Order):
    order = orders.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    
    # Update order data
    for field, value in updated_order.dict().items():
        setattr(order, field, value)
    
    return order

# Delete a order by ID
@app.delete("/orders/{order_id}", response_model=Order)
def delete_order(order_id: int):
    order = orders.pop(order_id, None)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    return order

  # uvicorn.run(app, host="0.0.0.0", port=port)
