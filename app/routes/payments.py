# Add these imports at the top
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.schemas.payment import (
    PaymentCreate, PaymentResponse, OrderCreateResponse, 
    RefundCreate, RefundResponse
)
from app.services.razorpay_service import razorpay_service
from app.models.payment import Payment
from app.config import settings

# For database, you would typically use a dependency
# For simplicity, we'll use a mock database
router = APIRouter(prefix="/payments", tags=["payments"])

# In-memory storage for demo (use proper database in production)
payments_db = {}

@router.post("/create-order", response_model=OrderCreateResponse)
async def create_order(payment_data: PaymentCreate):
    """
    Create a Razorpay order
    """
    try:
        # Create order in Razorpay
        order = razorpay_service.create_order(
            amount=payment_data.amount,
            currency=payment_data.currency,
            notes={
                "customer_name": payment_data.customer_name,
                "customer_email": payment_data.customer_email,
                "customer_phone": payment_data.customer_phone,
                "description": payment_data.description
            }
        )
        
        # Store in database (simplified)
        payment_record = {
            "order_id": order["id"],
            "amount": payment_data.amount,
            "currency": payment_data.currency,
            "status": "created",
            "customer_name": payment_data.customer_name,
            "customer_email": payment_data.customer_email,
            "customer_phone": payment_data.customer_phone,
            "description": payment_data.description
        }
        payments_db[order["id"]] = payment_record
        
        return OrderCreateResponse(
            order_id=order["id"],
            amount=payment_data.amount,
            currency=payment_data.currency,
            key_id=settings.razorpay_key_id,
            customer_name=payment_data.customer_name,
            customer_email=payment_data.customer_email
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create order: {str(e)}"
        )

@router.post("/verify-payment")
async def verify_payment(
    order_id: str,
    payment_id: str,
    signature: str
):
    """
    Verify payment signature after successful payment
    """
    try:
        # Verify signature
        is_valid = razorpay_service.verify_payment_signature(
            order_id, payment_id, signature
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment signature"
            )
        
        # Update payment status in database
        if order_id in payments_db:
            payments_db[order_id].update({
                "status": "paid",
                "razorpay_payment_id": payment_id,
                "razorpay_order_id": order_id,
                "razorpay_signature": signature
            })
        
        # Fetch payment details from Razorpay
        payment_details = razorpay_service.fetch_payment(payment_id)
        
        return {
            "status": "success",
            "payment_id": payment_id,
            "order_id": order_id,
            "payment_details": payment_details
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment verification failed: {str(e)}"
        )

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def razorpay_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle Razorpay webhook events
    """
    try:
        # Get webhook signature
        signature = request.headers.get("X-Razorpay-Signature")
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing signature"
            )
        
        # Read raw body
        body = await request.body()
        
        # Verify webhook signature
        if not razorpay_service.verify_webhook_signature(body, signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature"
            )
        
        # Parse webhook payload
        payload = await request.json()
        event = payload.get("event")
        
        # Process webhook event in background
        background_tasks.add_task(process_webhook_event, event, payload)
        
        return {"status": "Webhook processed successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook processing failed: {str(e)}"
        )

def process_webhook_event(event: str, payload: dict):
    """
    Process different webhook events
    """
    try:
        if event == "payment.captured":
            payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
            payment_id = payment_entity.get("id")
            order_id = payment_entity.get("order_id")
            
            # Update payment status in database
            for order_key, payment_data in payments_db.items():
                if payment_data.get("order_id") == order_id:
                    payments_db[order_key].update({
                        "status": "paid",
                        "razorpay_payment_id": payment_id,
                        "method": payment_entity.get("method")
                    })
                    break
        
        elif event == "payment.failed":
            payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
            order_id = payment_entity.get("order_id")
            
            # Update payment status to failed
            for order_key, payment_data in payments_db.items():
                if payment_data.get("order_id") == order_id:
                    payments_db[order_key]["status"] = "failed"
                    break
        
        elif event == "refund.created":
            refund_entity = payload.get("payload", {}).get("refund", {}).get("entity", {})
            payment_id = refund_entity.get("payment_id")
            
            # Update refund status
            for payment_data in payments_db.values():
                if payment_data.get("razorpay_payment_id") == payment_id:
                    payment_data.update({
                        "refund_id": refund_entity.get("id"),
                        "refund_amount": refund_entity.get("amount", 0) / 100,
                        "refund_status": "created"
                    })
                    break
        
        print(f"Processed webhook event: {event}")
        
    except Exception as e:
        print(f"Error processing webhook event: {str(e)}")

@router.post("/refund", response_model=RefundResponse)
async def create_refund(refund_data: RefundCreate):
    """
    Create a refund for a payment
    """
    try:
        # Create refund in Razorpay
        refund = razorpay_service.create_refund(
            payment_id=refund_data.payment_id,
            amount=refund_data.amount,
            notes=refund_data.notes
        )
        
        # Update database
        for payment_data in payments_db.values():
            if payment_data.get("razorpay_payment_id") == refund_data.payment_id:
                payment_data.update({
                    "refund_id": refund["id"],
                    "refund_amount": refund["amount"] / 100,
                    "refund_status": refund["status"],
                    "status": "refunded"
                })
                break
        
        return RefundResponse(
            refund_id=refund["id"],
            payment_id=refund_data.payment_id,
            amount=refund["amount"] / 100,
            status=refund["status"],
            speed=refund.get("speed", "normal"),
            created_at=refund["created_at"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Refund failed: {str(e)}"
        )

@router.get("/{payment_id}")
async def get_payment(payment_id: str):
    """
    Get payment details
    """
    payment_data = None
    for data in payments_db.values():
        if data.get("razorpay_payment_id") == payment_id:
            payment_data = data
            break
    
    if not payment_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment_data

@router.get("/")
async def list_payments():
    """
    List all payments
    """
    return list(payments_db.values())

# Add this route to your existing payments.py
@router.get("/test/client", response_class=HTMLResponse)
async def test_client():
    """
    Serve a test HTML client for payment testing
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Razorpay Test Client</title>
        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 600px; margin: 0 auto; }
            .card { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 8px; }
            button { background: #3399cc; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #2978a0; }
            .success { color: green; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 Razorpay Test Client</h1>
            
            <div class="card">
                <h3>1. Create Test Order</h3>
                <button onclick="createOrder()">Create ₹100 Test Order</button>
                <div id="orderResult"></div>
            </div>

            <div class="card">
                <h3>2. Payment Status</h3>
                <div id="paymentStatus"></div>
            </div>

            <div class="card">
                <h3>3. Test Cards</h3>
                <div style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
                    <h4>✅ Successful Payments:</h4>
                    <p><strong>Visa:</strong> 4111 1111 1111 1111</p>
                    <p><strong>MasterCard:</strong> 5104 0600 0000 0008</p>
                    <p><strong>Expiry:</strong> Any future date</p>
                    <p><strong>CVV:</strong> 123</p>
                    <p><strong>OTP:</strong> 123456</p>
                    
                    <h4>❌ Failed Payments:</h4>
                    <p><strong>Failure Card:</strong> 4111 1111 1111 1115</p>
                </div>
            </div>
        </div>

        <script>
            async function createOrder() {
                try {
                    document.getElementById('orderResult').innerHTML = '<p>Creating order...</p>';
                    
                    const response = await fetch('/payments/create-order', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            amount: 100.0,
                            currency: "INR",
                            customer_name: "Test User",
                            customer_email: "test@example.com",
                            description: "Test payment from Razorpay"
                        })
                    });

                    const orderData = await response.json();
                    document.getElementById('orderResult').innerHTML = `
                        <p class="success">✅ Order Created Successfully!</p>
                        <p><strong>Order ID:</strong> ${orderData.order_id}</p>
                        <button onclick="initiatePayment('${orderData.order_id}', '${orderData.key_id}')">
                            🔗 Proceed to Payment
                        </button>
                    `;
                } catch (error) {
                    document.getElementById('orderResult').innerHTML = `<p class="error">❌ Error creating order: ${error}</p>`;
                }
            }

            function initiatePayment(orderId, keyId) {
                const options = {
                    key: keyId,
                    amount: 10000,
                    currency: "INR",
                    name: "Test Merchant",
                    description: "Test Transaction",
                    order_id: orderId,
                    handler: function (response) {
                        document.getElementById('paymentStatus').innerHTML = `
                            <div style="background: #d4edda; padding: 15px; border-radius: 5px;">
                                <p class="success">✅ Payment Successful!</p>
                                <p><strong>Payment ID:</strong> ${response.razorpay_payment_id}</p>
                                <p><strong>Order ID:</strong> ${response.razorpay_order_id}</p>
                                <button onclick="verifyPayment('${response.razorpay_order_id}', '${response.razorpay_payment_id}', '${response.razorpay_signature}')">
                                    🔍 Verify Payment Signature
                                </button>
                            </div>
                        `;
                    },
                    "prefill": {
                        "name": "Test User",
                        "email": "test@example.com",
                        "contact": "9999999999"
                    },
                    "notes": {
                        "address": "Test Address"
                    },
                    "theme": {
                        "color": "#3399cc"
                    }
                };

                const rzp = new Razorpay(options);
                rzp.on('payment.failed', function (response) {
                    document.getElementById('paymentStatus').innerHTML = `
                        <div style="background: #f8d7da; padding: 15px; border-radius: 5px;">
                            <p class="error">❌ Payment Failed</p>
                            <p><strong>Error:</strong> ${response.error.description}</p>
                            <p><strong>Code:</strong> ${response.error.code}</p>
                        </div>
                    `;
                });
                rzp.open();
            }

            async function verifyPayment(orderId, paymentId, signature) {
                try {
                    const response = await fetch('/payments/verify-payment?order_id=' + orderId + '&payment_id=' + paymentId + '&signature=' + signature);
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        document.getElementById('paymentStatus').innerHTML += `
                            <div style="background: #d1ecf1; padding: 15px; margin-top: 10px; border-radius: 5px;">
                                <p class="success">✅ Signature Verification Successful!</p>
                                <details>
                                    <summary>View Payment Details</summary>
                                    <pre>${JSON.stringify(result, null, 2)}</pre>
                                </details>
                            </div>
                        `;
                    } else {
                        document.getElementById('paymentStatus').innerHTML += `<p class="error">❌ Signature Verification Failed</p>`;
                    }
                } catch (error) {
                    document.getElementById('paymentStatus').innerHTML += `<p class="error">❌ Verification Error: ${error}</p>`;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)