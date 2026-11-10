from fastapi import FastAPI
from sqlalchemy.orm import Session
from data_schemas import ProductRequest

from sqlalchemy import create_engine,select,insert
from models import Base,Product,User


app = FastAPI()

# Create a database using sqlalchemy engine
engine = create_engine("sqlite:///./duka-fastapi.db", echo=True)

# Create tales into the database using sqlalchemy
Base.metadata.create_all(engine)

# create a session to do sql transactions
session = Session(engine)

@app.get("/")
def home():
    return {"Duka FastAPI Version": "1.0"}

def add_user():
    user = User(
        full_name = "Mishi Wanjohi",
        email = "mishi@gmail.com",
        password = "hgyt123",
        phone_number = "0712345678"
    )
    session.add(user)
    session.commit()

add_user()


@app.post("/products")
def create_product(prod: ProductRequest):
    # store in the database
    new_product= Product(
        user_id=prod.user_id,
        product_name=prod.product_name,
        buying_price=prod.buying_price,
        selling_price=prod.selling_price,
        stock_quantity=prod.stock_quantity)

    session.add(new_product)
    session.commit()

    return {"new_product":new_product}