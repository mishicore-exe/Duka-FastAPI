from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select
from fastapi.middleware.cors import CORSMiddleware

from data_schemas import (
    ProductRequest, ProductResponse,
    SaleRequest, SaleResponse,
    Sales_detailRequest, Sales_detailResponse,
    PurchaseRequest, PurchaseResponse,
    PaymentRequest, PaymentResponse,
    LoginRequest, LoginResponse,
    RegisterRequest, RegisterResponse,
    STKPushRequest
)

from models import Base, Product, User, Sale, Sales_detail, Purchase, Payment
from myjwt import verify_password, create_access_token, get_password_hash, get_current_user
from mpesa import make_stk_push
from generate_receipts import create_pdf

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5500",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

engine = create_engine(
    "sqlite:///./duka-fastapi.db",
    connect_args={"check_same_thread": False}
)

Base.metadata.create_all(engine)

def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

def get_user(db: Session, email: str):
    return db.scalars(
        select(User).where(User.email == email)
    ).first()

@app.get("/")
def home():
    return {"Duka FastAPI Version": "1.0"}

# Authentication routes

@app.post("/register", response_model=RegisterResponse)
def register(user: RegisterRequest, db: Session = Depends(get_db)):
    db_user = get_user(db, user.email)

    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    db_user = User(
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
        password=get_password_hash(user.password)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    db_user.token = create_access_token({"sub": db_user.email})

    return db_user

@app.post("/login", response_model=LoginResponse)
def login(user: LoginRequest, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    db_user = get_user(db, user.email)

    if not db_user:
        raise credentials_exception

    if not verify_password(user.password, db_user.password):
        raise credentials_exception

    db_user.token = create_access_token({"sub": db_user.email})

    return db_user

# Product routes

@app.post("/products", response_model=ProductResponse)
def create_product(
    prod: ProductRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user(db, current_user)

    dbprod = Product(
        user_id=user.id,
        product_name=prod.product_name,
        buying_price=prod.buying_price,
        selling_price=prod.selling_price,
        stock_quantity=prod.stock_quantity
    )

    db.add(dbprod)
    db.commit()
    db.refresh(dbprod)

    return dbprod

@app.get("/products", response_model=list[ProductResponse])
def get_products(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user(db, current_user)

    products = db.scalars(
        select(Product).where(Product.user_id == user.id)
    ).all()

    return products

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_single_product(
    product_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user(db, current_user)

    product = db.scalars(
        select(Product).where(
            Product.id == product_id,
            Product.user_id == user.id
        )
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    prod: ProductRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user(db, current_user)

    product = db.scalars(
        select(Product).where(
            Product.id == product_id,
            Product.user_id == user.id
        )
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.product_name = prod.product_name
    product.buying_price = prod.buying_price
    product.selling_price = prod.selling_price
    product.stock_quantity = prod.stock_quantity

    db.commit()
    db.refresh(product)

    return product

# Sales routes

@app.post("/sales", response_model=SaleResponse)
def create_sale(
    sale: SaleRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user(db, current_user)

    product = db.scalars(
        select(Product).where(
            Product.id == sale.product_id,
            Product.user_id == user.id
        )
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if sale.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    if product.stock_quantity < sale.quantity:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )

    try:
        dbsale = Sale(
            user_id=user.id,
            product_id=sale.product_id,
            quantity=sale.quantity
        )

        product.stock_quantity -= sale.quantity

        db.add(dbsale)
        db.commit()
        db.refresh(dbsale)

        return dbsale

    except Exception as e:
        db.rollback()
        print("SALE ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to create sale"
        )

@app.get("/sales", response_model=list[SaleResponse])
def get_sale(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user(db, current_user)

    sales = db.scalars(
        select(Sale).where(Sale.user_id == user.id)
    ).all()

    return sales

@app.get("/sales/{sale_id}", response_model=SaleResponse)
def get_single_sale(
    sale_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user(db, current_user)

    sale = db.scalars(
        select(Sale).where(
            Sale.id == sale_id,
            Sale.user_id == user.id
        )
    ).first()

    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    return sale

# Sales detail routes

@app.post("/sales_detail", response_model=Sales_detailResponse)
def create_sale_detail(
    sale_detail: Sales_detailRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user(db, current_user)

    sale = db.scalars(
        select(Sale).where(
            Sale.id == sale_detail.sale_id,
            Sale.user_id == user.id
        )
    ).first()

    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    dbsale_d = Sales_detail(
        sale_id=sale_detail.sale_id,
        product_id=sale_detail.product_id,
        quantity=sale_detail.quantity
    )

    db.add(dbsale_d)
    db.commit()
    db.refresh(dbsale_d)

    return dbsale_d

@app.get("/sales_detail", response_model=list[Sales_detailResponse])
def get_sales_detail(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user(db, current_user)

    sales_d = db.scalars(
        select(Sales_detail)
        .join(Sale, Sales_detail.sale_id == Sale.id)
        .where(Sale.user_id == user.id)
    ).all()

    return sales_d

# Purchase routes

@app.post("/purchases", response_model=PurchaseResponse)
def create_purchase(
    purchase: PurchaseRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user(db, current_user)

    product = db.scalars(
        select(Product).where(
            Product.id == purchase.product_id,
            Product.user_id == user.id
        )
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    dbpurchase = Purchase(
        product_id=purchase.product_id,
        purchase_price=purchase.purchase_price
    )

    db.add(dbpurchase)
    db.commit()
    db.refresh(dbpurchase)

    return dbpurchase

@app.get("/purchases", response_model=list[PurchaseResponse])
def get_purchase(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user(db, current_user)

    purchases = db.scalars(
        select(Purchase)
        .join(Product, Purchase.product_id == Product.id)
        .where(Product.user_id == user.id)
    ).all()

    return purchases

# Payments routes

@app.post("/payments", response_model=PaymentResponse)
def create_payment(
    payment: PaymentRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user(db, current_user)

    sale = db.scalars(
        select(Sale).where(
            Sale.id == payment.sale_id,
            Sale.user_id == user.id
        )
    ).first()

    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    dbpayment = Payment(
        sale_id=payment.sale_id,
        amount_paid=payment.amount_paid,
        transaction_code=payment.transaction_code,
        mrid=payment.mrid,
        crid=payment.crid,
        payment_status=payment.payment_status,
        phone_number=payment.phone_number
    )

    db.add(dbpayment)
    db.commit()
    db.refresh(dbpayment)

    return dbpayment

@app.get("/payments", response_model=list[PaymentResponse])
def get_payments(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user(db, current_user)

    payments = db.scalars(
        select(Payment)
        .join(Sale, Payment.sale_id == Sale.id)
        .where(Sale.user_id == user.id)
    ).all()

    return payments

@app.get("/payment/{payment_id}", response_model=PaymentResponse)
def get_single_payment(
    payment_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = get_user(db, current_user)

    payment = db.scalars(
        select(Payment)
        .join(Sale, Payment.sale_id == Sale.id)
        .where(
            Payment.id == payment_id,
            Sale.user_id == user.id
        )
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return payment

# M-Pesa STK Push route

@app.post("/stk_push")
def stk_push(
    payload: STKPushRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        user = get_user(db, current_user)

        sale = db.scalars(
            select(Sale).where(
                Sale.id == payload.sale_id,
                Sale.user_id == user.id
            )
        ).first()

        if not sale:
            raise HTTPException(
                status_code=404,
                detail="Sale not found"
            )

        product = db.get(Product, sale.product_id)

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        amount = product.selling_price * sale.quantity

        response = make_stk_push({
            "sale_id": sale.id,
            "amount_paid": amount,
            "phone_number": payload.phone_number
        })

        print("STK PUSH RESPONSE:", response, flush=True)

        if response.get("ResponseCode") != "0":
            raise HTTPException(
                status_code=400,
                detail=response.get("ResponseDescription", "STK Push failed")
            )

        if not response.get("MerchantRequestID") or not response.get("CheckoutRequestID"):
            raise HTTPException(
                status_code=400,
                detail="Safaricom did not return request IDs"
            )

        new_payment = Payment(
            sale_id=sale.id,
            amount_paid=amount,
            phone_number=payload.phone_number,
            mrid=response["MerchantRequestID"],
            crid=response["CheckoutRequestID"],
            payment_status="pending"
        )

        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)

        print("PAYMENT CREATED:", new_payment.id, flush=True)

        return {
            "message": "STK Push initiated successfully",
            "payment_id": new_payment.id,
            "sale_id": sale.id,
            "MerchantRequestID": new_payment.mrid,
            "CheckoutRequestID": new_payment.crid,
            "payment_status": new_payment.payment_status
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        print("STK PUSH ERROR:", repr(e), flush=True)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# M-Pesa callback route

@app.post("/saf-callback")
def saf_callback(
    callback: dict,
    db: Session = Depends(get_db)
):
    try:
        stk_callback = callback.get("Body", {}).get("stkCallback", {})

        checkout_request_id = stk_callback.get("CheckoutRequestID")
        result_code = stk_callback.get("ResultCode")
        result_desc = stk_callback.get("ResultDesc")

        if not checkout_request_id:
            return {"Result": "Missing CheckoutRequestID"}

        payment = db.scalars(
            select(Payment).where(
                Payment.crid == checkout_request_id
            )
        ).first()

        if not payment:
            return {"Result": "Payment not found"}

        if result_code == 0:
            metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])

            transaction_code = None
            callback_amount = None
            phone_number = None

            for item in metadata:
                if item.get("Name") == "MpesaReceiptNumber":
                    transaction_code = item.get("Value")

                elif item.get("Name") == "Amount":
                    callback_amount = item.get("Value")

                elif item.get("Name") == "PhoneNumber":
                    phone_number = item.get("Value")

            if not transaction_code:
                return {"Result": "Transaction receipt missing"}

            payment.transaction_code = transaction_code
            payment.payment_status = "completed"

            if callback_amount is not None:
                payment.amount_paid = callback_amount

            if phone_number is not None:
                payment.phone_number = str(phone_number)

            db.commit()
            db.refresh(payment)

            print("PAYMENT UPDATED:", payment.transaction_code, flush=True)

            try:
                sale = db.get(Sale, payment.sale_id)
                user = db.get(User, sale.user_id) if sale else None

                receipt_text = (
                    "DUKA PAYMENT RECEIPT\n\n"
                    f"Sale ID: {payment.sale_id}\n"
                    f"Transaction Code: {payment.transaction_code}\n"
                    f"Amount Paid: KSh {payment.amount_paid}\n"
                    f"Phone Number: {payment.phone_number}\n"
                    f"Payment Status: {payment.payment_status}"
                )

                if user:
                    receipt_url = create_pdf(
                        receipt_text,
                        payment.transaction_code,
                        user.email
                    )
                    print("RECEIPT URL:", receipt_url, flush=True)

            except Exception as e:
                print("RECEIPT ERROR:", str(e), flush=True)

            return {"Result": "Payment completed successfully"}

        else:
            payment.payment_status = "failed"
            db.commit()

            print("PAYMENT FAILED:", result_desc, flush=True)

            return {
                "Result": "Payment failed",
                "Description": result_desc
            }

    except Exception as e:
        db.rollback()
        print("CALLBACK ERROR:", repr(e), flush=True)

        return {"Result": "Callback processing error"}