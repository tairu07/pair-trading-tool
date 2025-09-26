"""
Simplified FastAPI application for Vercel deployment
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI application
app = FastAPI(
    title="Pair Trading Tool API",
    description="API for managing pair trading strategies",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Pair Trading Tool API is running"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Pair Trading Tool API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Basic API endpoints
@app.get("/api/v1/pairs")
async def get_pairs():
    """Get pairs list"""
    return {"pairs": [], "message": "Pairs endpoint working"}

@app.get("/api/v1/status")
async def api_status():
    """API status"""
    return {
        "status": "running",
        "version": "1.0.0",
        "environment": os.getenv("VERCEL_ENV", "development")
    }

# Vercel handler function
def handler(request, response):
    return app(request, response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
