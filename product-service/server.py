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



class ProductModel(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)  # Use username instead of user_id
    name = Column(String, index=True)
    cost = Column(Integer)

# Create the SQLite database tables
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

# Pydantic model for product
class Product(BaseModel):
    name: str
    cost: int

# Create a new product
@app.post("/products/", response_model=Product)
async def create_product(product: Product, user: str = Depends(get_user)):
    async with database.transaction():
        product_id = await database.execute(ProductModel.__table__.insert().values(
            username=user, name=product.name, cost=product.cost
        ))
        return {"product_id": product_id, **product.dict()}

# Retrieve all products for the current user
@app.get("/products/")
async def read_products(user: str = Depends(get_user)):
    print("user is ", user)
    query = ProductModel.__table__.select().where(ProductModel.username == user)
    products_list = await database.fetch_all(query)
    # Create a list of dictionaries containing product ID and product details
    result = []
    for product in products_list:
        product_data = Product(**product)
        result.append({"product_id": product.id, "product_user": product.username, "product_details": product_data})
    return result

# Retrieve a specific product by ID for the current user
@app.get("/products/{product_id}", response_model=Product)
async def read_product(product_id: int, user: str = Depends(get_user)):
    query = ProductModel.__table__.select().where(ProductModel.id == product_id, ProductModel.username == user)
    product = await database.fetch_one(query)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

# Update an product by ID for the current user
@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, updated_product: Product, user: str = Depends(get_user)):
    print("user", user)
    query = ProductModel.__table__.update().where(ProductModel.id == product_id, ProductModel.username == user).values(
        name=updated_product.name, cost=updated_product.cost
    )
    try:
        affected_rows = await database.execute(query)
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        # Handle database execution errors here
        raise HTTPException(status_code=400, detail="Failed to update product")
    return updated_product

# Delete an product by ID for the current user
@app.delete("/products/{product_id}")
async def delete_product(product_id: int, user: str = Depends(get_user)):
    query = ProductModel.__table__.delete().where(ProductModel.id == product_id, ProductModel.username == user)
    try:
        affected_rows = await database.execute(query)
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        # Handle database execution errors here
        raise HTTPException(status_code=400, detail="Failed to delete product")
    return {"message": "product deleted sucessfully"}
