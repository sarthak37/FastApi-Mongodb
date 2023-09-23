from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId
from typing import List
from datetime import datetime

class Address(BaseModel):
    city: str
    country: str
    zip_code: str

class Item(BaseModel):
    product_id: str
    bought_quantity: int

class Order(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    items: List[Item]
    user_address: Address




class Product(BaseModel):
    name: str
    price: float
    quantity: int

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
            }    

client = MongoClient("mongodb+srv://sarthak27998:qSeNbtxSicASAf5B@cluster0.t7zk8su.mongodb.net/ff?retryWrites=true&w=majority")

db = client.test

app = FastAPI()

@app.post("/product/")
async def create_product(product: Product):
    if db.product.find_one({"name": product.name}):
        raise HTTPException(status_code=400, detail="Product already exists")
    
    product_dict = product.dict()
    product_dict["_id"] = str(ObjectId())  # Convert ObjectId to string
    db.product.insert_one(product_dict)
    
    # Return the product with _id as a string
    return {"_id": product_dict["_id"], **product_dict}


@app.get("/product/")
async def read_all_products():
    products = []
    for product in db.product.find():
        product["_id"] = str(product["_id"])
        products.append(product)
    return products    

@app.get("/product/{product_id}")
async def read_product(product_id: str):
    product_data = db.product.find_one({"_id": product_id})
    if product_data is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_data

@app.put("/product/{product_id}")
async def update_product(product_id: str, product: Product):
    if db.product.find_one({"_id": product_id}) is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.product.update_one({"_id": product_id}, {"$set": product.dict()})
    return {"message": "Product updated successfully"}

@app.delete("/product/{product_id}")
async def delete_product(product_id: str):
    if db.product.find_one({"_id": product_id}) is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.product.delete_one({"_id": product_id})
    return {"message": "Product deleted successfully"}

@app.post("/order/")
async def create_order(order: Order):
    total_cost = 0
    items = []
    for item in order.items:
        product_data = db.product.find_one({"_id": item.product_id})
        if product_data is None:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product_data["quantity"] < item.bought_quantity:
            raise HTTPException(status_code=400, detail=f"Not enough quantity for product {item.product_id}")
        total_cost += product_data["price"] * item.bought_quantity
        db.product.update_one({"_id": item.product_id}, {"$inc": {"quantity": -item.bought_quantity}})
        items.append({"name": product_data["name"], "product_id": item.product_id, "bought_quantity": item.bought_quantity})
    order_dict = order.dict()
    order_dict["_id"] = str(ObjectId())
    order_dict["total_amount"] = total_cost
    order_dict["items"] = items
    db.order.insert_one(order_dict)
    return order_dict

@app.put("/order/{order_id}")
async def update_order(order_id: str, order: Order):
    if db.order.find_one({"_id": order_id}) is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Get the existing order
    existing_order = db.order.find_one({"_id": order_id})
    
    # Check if the quantity for each item in the order is available
    total_cost = 0
    for item in order.items:
        product_data = db.product.find_one({"_id": item.product_id})
        if product_data is None:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        # Find the corresponding item in the existing order
        existing_item = next((i for i in existing_order["items"] if i["product_id"] == item.product_id), None)
        
        if existing_item is not None:
            # Calculate the difference in quantity between the existing item and the updated item
            quantity_difference = item.bought_quantity - existing_item["bought_quantity"]
        else:
            # If the item is not in the existing order, the difference in quantity is the quantity of the item
            quantity_difference = item.bought_quantity
        
        if product_data["quantity"] < quantity_difference:
            raise HTTPException(status_code=400, detail=f"Not enough quantity for product {item.product_id}")
        
        # Update the quantity of the product
        db.product.update_one({"_id": item.product_id}, {"$inc": {"quantity": -quantity_difference}})
        
        # Add the cost of this item to the total cost
        total_cost += product_data["price"] * item.bought_quantity
    
    # Update the order
    order_dict = order.dict()
    order_dict["total_amount"] = total_cost
    db.order.update_one({"_id": order_id}, {"$set": order_dict})
    
    return {"message": "Order updated successfully"}
    
@app.delete("/order/{order_id}")
async def delete_order(order_id: str):
    if db.order.find_one({"_id": order_id}) is None:
        raise HTTPException(status_code=404, detail="Order not found")
    db.order.delete_one({"_id": order_id})
    return {"message": "Order deleted successfully"}     

@app.get("/order/")
async def read_all_orders(skip: int = 0, limit: int = 10):
    orders = []
    for order in db.order.find().skip(skip).limit(limit):
        order["_id"] = str(order["_id"])
        orders.append(order)
    return orders



@app.get("/order/{order_id}")
async def read_order(order_id: str):
    order_data = db.order.find_one({"_id": order_id})
    if order_data is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_data    