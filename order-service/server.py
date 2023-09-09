from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import sessionmaker
from databases import Database
from jose import JWTError, jwt
from typing import List, Dict

app = FastAPI()

# SQLite database configuration
DATABASE_URL = "sqlite:///../db/test.sqlite"
database = Database(DATABASE_URL)

# SQLAlchemy models
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


# Define OAuth2 password bearer scheme
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# JWT token verification function
async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token has expired or is invalid")
    return username



class OrderModel(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # Use username instead of user_id
    name = Column(String, index=True)
    cost = Column(Integer)

# Create the SQLite database tables
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

# JWT configuration
SECRET_KEY = "hefni-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pydantic model for order

class Order(BaseModel):
    name: str
    cost: int

# Create a new order
@app.post("/orders/", response_model=Order)
async def create_order(order: Order, current_user: str = Depends(verify_token)):
    async with database.transaction():
        order_id = await database.execute(OrderModel.__table__.insert().values(
            username=current_user, name=order.name, cost=order.cost
        ))
        return {"order_id": order_id, **order.dict()}

# Retrieve all orders for the current user
@app.get("/orders/", response_model=Dict[int, Order])
async def read_orders(current_user: str = Depends(verify_token)):
    query = OrderModel.__table__.select().where(OrderModel.username == current_user)
    orders_list = await database.fetch_all(query)
    return {order.id: Order(**order) for order in orders_list}

# Retrieve a specific order by ID for the current user
@app.get("/orders/{order_id}", response_model=Order)
async def read_order(order_id: int, current_user: str = Depends(verify_token)):
    query = OrderModel.__table__.select().where(OrderModel.id == order_id, OrderModel.username == current_user)
    order = await database.fetch_one(query)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**order)

# Update an order by ID for the current user
@app.put("/orders/{order_id}", response_model=Order)
async def update_order(order_id: int, updated_order: Order, current_user: str = Depends(verify_token)):
    query = OrderModel.__table__.update().where(OrderModel.id == order_id, OrderModel.username == current_user).values(
        name=updated_order.name, cost=updated_order.cost
    )
    await database.execute(query)
    return updated_order

# Delete an order by ID for the current user
@app.delete("/orders/{order_id}")
async def delete_order(order_id: int, current_user: str = Depends(verify_token)):
    query = OrderModel.__table__.delete().where(OrderModel.id == order_id, OrderModel.username == current_user)
    try:
        affected_rows = await database.execute(query)
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Order not found")
    except Exception as e:
        # Handle database execution errors here
        raise HTTPException(status_code=500, detail="Failed to delete order")

    # await database.execute(query)
    return {"message": "Order deleted"}

