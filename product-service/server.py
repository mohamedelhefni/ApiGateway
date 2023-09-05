from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# In-memory storage for products
products = {}

# Pydantic model for product
class Product(BaseModel):
    name: str
    price: float
    description: str

# Create a new product
@app.post("/products/", response_model=Product)
def create_product(product: Product):
    product_id = len(products) + 1
    products[product_id] = product
    return {"product_id": product_id, **product.dict()}

# Retrieve all products
@app.get("/products/", response_model=Dict[int, Product])
def read_products():
    return products

# Retrieve a specific product by ID
@app.get("/products/{product_id}", response_model=Product)
def read_product(product_id: int):
    product = products.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Update a product by ID
@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, updated_product: Product):
    product = products.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update product data
    for field, value in updated_product.dict().items():
        setattr(product, field, value)
    
    return product

# Delete a product by ID
@app.delete("/products/{product_id}", response_model=Product)
def delete_product(product_id: int):
    product = products.pop(product_id, None)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


