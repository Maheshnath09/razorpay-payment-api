from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    amount: float
    currency: str = "INR"
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = None
    description: Optional[str] = None

class PaymentResponse(BaseModel):
    id: int
    payment_id: str
    order_id: str
    amount: float
    currency: str
    status: str
    customer_email: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderCreateResponse(BaseModel):
    order_id: str
    amount: float
    currency: str
    key_id: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None

class WebhookPayload(BaseModel):
    event: str
    payload: dict

class RefundCreate(BaseModel):
    payment_id: str
    amount: Optional[float] = None  # Full refund if not specified
    notes: Optional[dict] = None

class RefundResponse(BaseModel):
    refund_id: str
    payment_id: str
    amount: float
    status: str
    speed: str
    created_at: int