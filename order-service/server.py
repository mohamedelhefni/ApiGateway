import os
from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from databases import Database

app = FastAPI()

# SQLite database configuration
DB_URI = os.getenv("DB_URI")
DATABASE_URL = f"sqlite:///{DB_URI}"
database = Database(DATABASE_URL)

# SQLAlchemy models
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Custom dependency to get user from request headers
async def get_user(request: Request):
    return request.headers.get('user')



class OrderModel(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # Use username instead of user_id
    name = Column(String, index=True)
    cost = Column(Integer)

# Create the SQLite database tables
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

# Pydantic model for order
class Order(BaseModel):
    name: str
    cost: int

# Create a new order
@app.post("/orders/", response_model=Order)
async def create_order(order: Order, user: str = Depends(get_user)):
    async with database.transaction():
        order_id = await database.execute(OrderModel.__table__.insert().values(
            username=user, name=order.name, cost=order.cost
        ))
        return {"order_id": order_id, **order.dict()}

# Retrieve all orders for the current user
@app.get("/orders/")
async def read_orders(user: str = Depends(get_user)):
    print("user is ", user)
    query = OrderModel.__table__.select().where(OrderModel.username == user)
    orders_list = await database.fetch_all(query)
    # Create a list of dictionaries containing order ID and order details
    result = []
    for order in orders_list:
        order_data = Order(**order)
        result.append({"order_id": order.id, "order_user": order.username, "order_details": order_data})
    return result

# Retrieve a specific order by ID for the current user
@app.get("/orders/{order_id}", response_model=Order)
async def read_order(order_id: int, user: str = Depends(get_user)):
    query = OrderModel.__table__.select().where(OrderModel.id == order_id, OrderModel.username == user)
    order = await database.fetch_one(query)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**order)

# Update an order by ID for the current user
@app.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, updated_order: Order, user: str = Depends(get_user)):
    print("user", user)
    query = OrderModel.__table__.update().where(OrderModel.id == order_id, OrderModel.username == user).values(
        name=updated_order.name, cost=updated_order.cost
    )
    try:
        affected_rows = await database.execute(query)
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        # Handle database execution errors here
        raise HTTPException(status_code=400, detail="Failed to update order")
    return updated_order

# Delete an order by ID for the current user
@app.delete("/orders/{order_id}")
async def delete_order(order_id: int, user: str = Depends(get_user)):
    query = OrderModel.__table__.delete().where(OrderModel.id == order_id, OrderModel.username == user)
    try:
        affected_rows = await database.execute(query)
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        # Handle database execution errors here
        raise HTTPException(status_code=400, detail="Failed to delete order")
    return {"message": "order deleted sucessfully"}
