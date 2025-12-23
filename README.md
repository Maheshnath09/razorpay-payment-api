# 💳 Razorpay Payment Gateway API

A complete **FastAPI** integration with **Razorpay** payment gateway, featuring order creation, payment verification, webhook handling, and refund management.

## 🚀 Features

- ✅ **Order Creation** - Create Razorpay orders with customer details
- ✅ **Payment Verification** - Secure signature verification for payments
- ✅ **Webhook Integration** - Handle real-time payment events
- ✅ **Refund Management** - Process full and partial refunds
- ✅ **Test Client** - Built-in HTML test interface
- ✅ **CORS Support** - Cross-origin requests enabled
- ✅ **SQLAlchemy Models** - Database integration ready
- ✅ **Pydantic Schemas** - Request/response validation

## 📋 Prerequisites

- Python 3.8+
- Razorpay Account ([Sign up here](https://razorpay.com/))
- API Keys from Razorpay Dashboard

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Maheshnath09/razorpay-payment-api.git
   cd razorpay-payment-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Update `.env` file with your Razorpay credentials:
   ```env
   RAZORPAY_KEY_ID=rzp_test_your_key_id
   RAZORPAY_KEY_SECRET=your_key_secret
   WEBHOOK_SECRET=your_webhook_secret
   DATABASE_URL=sqlite:///./payments.db
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Core Endpoints

#### 🔹 Create Order
```http
POST /payments/create-order
```

**Request Body:**
```json
{
  "amount": 100.0,
  "currency": "INR",
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "customer_phone": "+919999999999",
  "description": "Test payment"
}
```

**Response:**
```json
{
  "order_id": "order_xyz123",
  "amount": 100.0,
  "currency": "INR",
  "key_id": "rzp_test_xyz",
  "customer_name": "John Doe",
  "customer_email": "john@example.com"
}
```

#### 🔹 Verify Payment
```http
POST /payments/verify-payment?order_id={order_id}&payment_id={payment_id}&signature={signature}
```

**Response:**
```json
{
  "status": "success",
  "payment_id": "pay_xyz123",
  "order_id": "order_xyz123",
  "payment_details": { ... }
}
```

#### 🔹 Create Refund
```http
POST /payments/refund
```

**Request Body:**
```json
{
  "payment_id": "pay_xyz123",
  "amount": 50.0,
  "notes": {
    "reason": "Customer request"
  }
}
```

#### 🔹 Webhook Handler
```http
POST /payments/webhook
```
Handles Razorpay webhook events for real-time payment updates.

#### 🔹 Get Payment Details
```http
GET /payments/{payment_id}
```

#### 🔹 List All Payments
```http
GET /payments/
```

## 🧪 Testing

### Built-in Test Client
Visit `http://localhost:8000/payments/test/client` for an interactive test interface.

### Test HTML File
Use the included `test_frontend.html` file:
```bash
# Open test_frontend.html in your browser
# Make sure the API is running on localhost:8000
```

### Test Cards (Razorpay Test Mode)

**✅ Successful Payments:**
- **Visa**: `4111 1111 1111 1111`
- **MasterCard**: `5104 0600 0000 0008`
- **Expiry**: Any future date
- **CVV**: `123`
- **OTP**: `123456`

**❌ Failed Payments:**
- **Failure Card**: `4111 1111 1111 1115`

## 🏗️ Project Structure

```
Payement-api-razorpay/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   └── payment.py          # SQLAlchemy models
│   ├── routes/
│   │   ├── __init__.py
│   │   └── payments.py         # API endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── payment.py          # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── razorpay_service.py # Razorpay integration
│   ├── utils/
│   │   ├── __init__.py
│   │   └── security.py         # Security utilities
│   ├── __init__.py
│   ├── config.py               # Configuration settings
│   └── main.py                 # FastAPI application
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
├── test_frontend.html          # Test client
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `RAZORPAY_KEY_ID` | Your Razorpay Key ID | ✅ |
| `RAZORPAY_KEY_SECRET` | Your Razorpay Key Secret | ✅ |
| `WEBHOOK_SECRET` | Webhook signature secret | ✅ |
| `DATABASE_URL` | Database connection string | ❌ |

### Webhook Configuration

1. Go to Razorpay Dashboard → Settings → Webhooks
2. Add webhook URL: `https://yourdomain.com/payments/webhook`
3. Select events: `payment.captured`, `payment.failed`, `refund.created`
4. Copy the webhook secret to your `.env` file

## 🔒 Security Features

- **Signature Verification**: All payments verified using Razorpay signatures
- **Webhook Authentication**: Secure webhook signature validation
- **CORS Configuration**: Configurable cross-origin settings
- **Environment Variables**: Sensitive data stored securely

## 🚀 Deployment

### Production Checklist

1. **Update CORS settings** in `main.py`:
   ```python
   allow_origins=["https://yourdomain.com"]  # Replace with your domain
   ```

2. **Use production database**:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ```

3. **Set up HTTPS** for webhook endpoints

4. **Configure webhook URL** in Razorpay Dashboard

5. **Use production Razorpay keys**

### Docker Deployment (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📝 Usage Examples

### Frontend Integration (JavaScript)

```javascript
// Create order
const orderResponse = await fetch('/payments/create-order', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        amount: 100.0,
        currency: "INR",
        customer_name: "John Doe",
        customer_email: "john@example.com"
    })
});

const orderData = await orderResponse.json();

// Initialize Razorpay
const options = {
    key: orderData.key_id,
    amount: orderData.amount * 100,
    currency: orderData.currency,
    order_id: orderData.order_id,
    handler: function(response) {
        // Verify payment
        verifyPayment(response.razorpay_order_id, 
                     response.razorpay_payment_id, 
                     response.razorpay_signature);
    }
};

const rzp = new Razorpay(options);
rzp.open();
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Razorpay Documentation**: https://razorpay.com/docs/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Issues**: Create an issue in this repository

## 🔗 Links

- [Razorpay Dashboard](https://dashboard.razorpay.com/)
- [Razorpay Test Cards](https://razorpay.com/docs/payments/payments/test-card-upi-details/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**⚡ Quick Start**: Run `uvicorn app.main:app --reload` and visit `http://localhost:8000/payments/test/client` to test payments immediately!