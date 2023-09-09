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



class ProductModel(Base):
    __tablename__ = "products"
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

# Pydantic model for product

class Product(BaseModel):
    name: str
    cost: int

# Create a new product
@app.post("/products/", response_model=Product)
async def create_product(product: Product, current_user: str = Depends(verify_token)):
    async with database.transaction():
        product_id = await database.execute(ProductModel.__table__.insert().values(
            username=current_user, name=product.name, cost=product.cost
        ))
        return {"product_id": product_id, **product.dict()}

# Retrieve all products for the current user
@app.get("/products/", response_model=Dict[int, Product])
async def read_products(current_user: str = Depends(verify_token)):
    query = ProductModel.__table__.select().where(ProductModel.username == current_user)
    products_list = await database.fetch_all(query)
    return {product.id: Product(**product) for product in products_list}

# Retrieve a specific product by ID for the current user
@app.get("/products/{product_id}", response_model=Product)
async def read_product(product_id: int, current_user: str = Depends(verify_token)):
    query = ProductModel.__table__.select().where(ProductModel.id == product_id, ProductModel.username == current_user)
    product = await database.fetch_one(query)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

# Update an product by ID for the current user
@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, updated_product: Product, current_user: str = Depends(verify_token)):
    query = ProductModel.__table__.update().where(ProductModel.id == product_id, ProductModel.username == current_user).values(
        name=updated_product.name, cost=updated_product.cost
    )
    await database.execute(query)
    return updated_product

# Delete an product by ID for the current user
@app.delete("/products/{product_id}")
async def delete_product(product_id: int, current_user: str = Depends(verify_token)):
    query = ProductModel.__table__.delete().where(ProductModel.id == product_id, ProductModel.username == current_user)
    try:
        affected_rows = await database.execute(query)
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        # Handle database execution errors here
        raise HTTPException(status_code=500, detail="Failed to delete product")

    # await database.execute(query)
    return {"message": "Product deleted"}


