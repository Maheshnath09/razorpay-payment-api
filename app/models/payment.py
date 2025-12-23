from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String, unique=True, index=True)  # Razorpay payment ID
    order_id = Column(String, index=True)  # Razorpay order ID
    amount = Column(Float)
    currency = Column(String, default="INR")
    status = Column(String)  # created, attempted, paid, failed, refunded
    method = Column(String, nullable=True)  # payment method
    description = Column(Text, nullable=True)
    customer_name = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    
    # Razorpay response fields
    razorpay_signature = Column(String, nullable=True)
    razorpay_order_id = Column(String, nullable=True)
    razorpay_payment_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Refund fields
    refund_id = Column(String, nullable=True)
    refund_amount = Column(Float, nullable=True)
    refund_status = Column(String, nullable=True)