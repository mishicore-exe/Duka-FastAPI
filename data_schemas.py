from pydantic import BaseModel

class ProductRequest(BaseModel):
    user_id : int
    product_name : str
    buying_price : float
    selling_price : float
    stock_quantity : int

class ProductResponse(BaseModel):
    id : int
    user_id : int
    product_name : str
    buying_price : float
    selling_price : float
    stock_quantity : int

class UserRequest(BaseModel):
    full_name: str
    email: str
    password: str
    phone_number: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    password: str
    phone_number: str

class SaleRequest(BaseModel):
    user_id : int
    product_id : int
    quantity : int

class SaleResponse(BaseModel):
    id : int
    user_id : int
    product_id : int
    quantity : int

class Sales_detailRequest(BaseModel):
    sale_id : int
    product_id : int
    quantity : int

class Sales_detailResponse(BaseModel):
    id : int
    sale_id : int
    product_id : int
    quantity : int

class PurchaseRequest(BaseModel):
    product_id : int
    purchase_price : float

class PurchaseResponse(BaseModel):
    id : int
    product_id : int
    purchase_price : float

class PaymentRequest(BaseModel):
    sale_id : int
    amount_paid : float
    transaction_code : str 
    mrid : str
    crid : str
    payment_status : str 
    phone_number : str

class PaymentResponse(BaseModel):
    id : int
    sale_id : int
    amount_paid : float
    transaction_code : str 
    mrid : str
    crid : str
    payment_status : str
    phone_number : str
