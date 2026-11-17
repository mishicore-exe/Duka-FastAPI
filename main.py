from fastapi import FastAPI,HTTPException
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

# Product routes

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

# fetching single product
@app.get("/products/{product_id}", response_model=ProductResponse)
def get_single_product(product_id):
    query = select(Product).where(Product.id == product_id)
    product = session.scalars(query).first()
    
    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    return product

# update product
@app.put("/products/{product_id}", response_model= ProductResponse)
def update_product(product_id : int , prod : ProductRequest):
    query = select(Product).where(Product.id == product_id)
    product = session.scalars(query).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    product.product_name = prod.product_name
    product.buying_price = prod.buying_price
    product.selling_price = prod.selling_price
    product.stock_quantity = prod.stock_quantity

    session.commit()
    return product

# End Product routes

# Sales routes

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

# update sale
@app.put("/sales/{sale_id}", response_model= SaleResponse)
def update_sale(sale_id : int , sal : SaleRequest):
    query = select(Sale).where(Sale.id == sale_id)
    sale = session.scalars(query).first()

    if sale is None:
            raise HTTPException(
                status_code=404,
                detail="Sale not found"
            )
    sale.user_id= sal.user_id
    sale.product_id = sal.product_id
    sale.quantity = sal.quantity
    
    session.commit()
    return sale

# fetch single sale
@app.get("/sales/{sale_id}", response_model=SaleResponse)
def get_single_sale(sale_id):
    query = select(Sale).where(Sale.id == sale_id)
    sale = session.scalars(query).first()
    
    if sale is None:
        raise HTTPException(
            status_code=404,
            detail="Sale not found"
        )
    return sale
# End Sales routes

# Sales_detail routes

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

# update sale_detail
@app.put("/sales_detail/{SalesDetail_id}", response_model= Sales_detailResponse)
def update_SalesDetail(sale_detail_id : int , sale_d : Sales_detailRequest):
    query = select(Sales_detail).where(Sales_detail.id == sale_detail_id)
    sales_detail = session.scalars(query).first()

    if sales_detail is None:
            raise HTTPException(
                status_code=404,
                detail="Sales detail not found"
            )
    sales_detail.sale_id= sale_d.sale_id
    sales_detail.product_id = sale_d.product_id
    sales_detail.quantity = sale_d.quantity
    
    session.commit()
    return sales_detail

# fetch single sale_detail
@app.get("/sales_detail/{SalesDetail_id}", response_model=Sales_detailResponse)
def get_single_SaleDetail(SalesDetail_id: int):
    query = select(Sales_detail).where(Sales_detail.id == SalesDetail_id)
    sale_d = session.scalars(query).first()

    if sale_d is None:
        raise HTTPException(
            status_code=404,
            detail="Sales detail not found"
        )
    return sale_d

# End Sales_details routes

# Purchase routes

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

# update purchase
@app.put("/purchases/{purchase_id}", response_model= PurchaseResponse)
def update_purchase(purchase_id : int , pur : PurchaseRequest):
    query = select(Purchase).where(Purchase.id == purchase_id)
    purchase = session.scalars(query).first()

    if purchase is None:
            raise HTTPException(
                status_code=404,
                detail="Purchase not found"
            )
    purchase.product_id= pur.product_id
    purchase.purchase_price= pur.purchase_price
    
    session.commit()
    return purchase

# fetch single purchase
@app.get("/purchase/{purchase_id}", response_model=PurchaseResponse)
def get_single_purchase(purchase_id):
    query = select(Purchase).where(Purchase.id == purchase_id)
    purchase = session.scalars(query).first()
    
    if purchase is None:
        raise HTTPException(
            status_code=404,
            detail="Purchase not found"
        )
    return purchase

# End Purchase routes

# Payments routes

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

# update payments
@app.put("/payments/{payment_id}", response_model= PaymentResponse)
def update_payment(payment_id : int , pay : PaymentRequest):
    query = select(Payment).where(Payment.id == payment_id)
    payment = session.scalars(query).first()

    if payment is None:
            raise HTTPException(
                status_code=404,
                detail="Payment not found"
            )
    payment.sale_id= pay.sale_id
    payment.amount_paid= pay.amount_paid
    payment.transaction_code= pay.transaction_code
    payment.mrid= pay.mrid
    payment.crid= pay.crid
    payment.payment_status= pay.payment_status
    payment.phone_number= pay.phone_number
    
    session.commit()
    return payment

# fetch single payment
@app.get("/payment/{payment_id}", response_model=PaymentResponse)
def get_single_payment(payment_id):
    query = select(Payment).where(Payment.id == payment_id)
    payment = session.scalars(query).first()
    
    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )
    return payment

# End payments routes
