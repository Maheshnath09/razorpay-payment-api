from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Adding CORS middleware for cross-origin 
from app.routes import payments

app = FastAPI(
    title="Razorpay Payment Gateway API",
    description="Complete Razorpay integration with FastAPI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (change in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(payments.router)

@app.get("/")
async def root():
    return {
        "message": "Razorpay Payment Gateway API",
        "status": "active",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)