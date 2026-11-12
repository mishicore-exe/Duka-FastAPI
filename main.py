from fastapi import FastAPI
from sqlalchemy.orm import Session
from data_schemas import ProductRequest,ProductResponse,SaleRequest,SaleResponse,Sales_detailRequest,Sales_detailResponse,PurchaseRequest,PurchaseResponse,PaymentResponse,PaymentRequest
from sqlalchemy import create_engine,select
from models import Base,Product,User,Sale,Sales_detail,Purchase,Payment

app = FastAPI()

# Create a database using sqlalchemy engine
engine = create_engine("sqlite:///./duka-fastapi.db", echo=True)

# Create tables into the database using sqlalchemy
Base.metadata.create_all(engine)

# Create a session to do SQL transactions
session = Session(engine)

@app.get("/")
def home():
    return {"Duka FastAPI Version": "1.0"}

def add_user():
    user = User(
        full_name="Mishi Wanjohi",
        email="mishi@gmail.com",
        password="hgyt123",
        phone_number="0712345678"
    )
    session.add(user)
    session.commit()
    return user

@app.post("/products", response_model=ProductResponse)
def create_product(prod: ProductRequest):
    dbprod = Product(
        user_id=prod.user_id,
        product_name=prod.product_name,
        buying_price=prod.buying_price,
        selling_price=prod.selling_price,
        stock_quantity=prod.stock_quantity
    )
    session.add(dbprod)
    session.commit()
    return dbprod

@app.get("/products", response_model=list[ProductResponse])
def get_products():
    query = select(Product)
    products = session.scalars(query)
    return products

@app.post("/sales", response_model=SaleResponse)
def create_sale(sale: SaleRequest):
    dbsale = Sale(
        user_id=sale.user_id,
        product_id=sale.product_id,
        quantity=sale.quantity
    )
    session.add(dbsale)
    session.commit()
    return dbsale

@app.get("/sales", response_model=list[SaleResponse])
def get_sale():
    query = select(Sale)
    sales = session.scalars(query)
    return sales

@app.post("/sales_detail", response_model=Sales_detailResponse)
def create_sale_detail(sale_detail: Sales_detailRequest):
    dbsale_d = Sales_detail(
        sale_id=sale_detail.sale_id,
        product_id=sale_detail.product_id,
        quantity=sale_detail.quantity
    )
    session.add(dbsale_d)
    session.commit()
    return dbsale_d

@app.get("/sales_detail", response_model=list[Sales_detailResponse])
def get_sales_detail():
    query = select(Sales_detail)
    sales_d = session.scalars(query)
    return sales_d

@app.post("/purchases", response_model=PurchaseResponse)
def create_purchase(purchase: PurchaseRequest):
    dbpurchase = Purchase(
        product_id=purchase.product_id,
        purchase_price=purchase.purchase_price
    )
    session.add(dbpurchase)
    session.commit()
    return dbpurchase

@app.get("/purchases", response_model=list[PurchaseResponse])
def get_purchase():
    query = select(Purchase)
    purchases = session.scalars(query)
    return purchases

@app.post("/payments", response_model=PaymentResponse)
def create_payment(payment: PaymentRequest):
    dbpayment = Payment(
        sale_id=payment.sale_id,
        amount_paid=payment.amount_paid,
        transaction_code=payment.transaction_code,
        mrid=payment.mrid,
        crid=payment.crid,
        payment_status=payment.payment_status,
        phone_number=payment.phone_number
    )
    session.add(dbpayment)
    session.commit()
    return dbpayment

@app.get("/payments", response_model=list[PaymentResponse])
def get_payments():
    query = select(Payment)
    payments = session.scalars(query)
    return payments
