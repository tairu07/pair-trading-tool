"""
FastAPI application for Pair Trading Tool
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# API routers
import api.pairs as pairs_api
import api.backtest as backtest_api
import api.alerts as alerts_api
import api.market_data as market_data_api

# Background services
from websocket_server import websocket_manager, handle_websocket_message
from scheduler import scheduler
from notifications import notification_manager

# Database
from database import engine
from models import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Pair Trading Tool API...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    
    # Start background services
    scheduler_task = asyncio.create_task(scheduler.start())
    websocket_task = asyncio.create_task(websocket_manager.start_monitoring())
    
    logger.info("Background services started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Pair Trading Tool API...")
    
    # Stop background services
    await scheduler.stop()
    await websocket_manager.stop_monitoring()
    
    # Cancel tasks
    scheduler_task.cancel()
    websocket_task.cancel()
    
    try:
        await asyncio.gather(scheduler_task, websocket_task, return_exceptions=True)
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        
    logger.info("Shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="Pair Trading Tool API",
    description="API for managing pair trading strategies, monitoring, and backtesting",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
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


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection endpoint"""
    await websocket.accept()
    await websocket_manager.register(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            await handle_websocket_message(websocket, data)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket_manager.unregister(websocket)

# System control endpoints
@app.post("/api/system/start-monitoring")
async def start_monitoring():
    """Start real-time monitoring"""
    if not websocket_manager.monitoring_active:
        asyncio.create_task(websocket_manager.start_monitoring())
        return {"message": "Monitoring started"}
    else:
        return {"message": "Monitoring already active"}

@app.post("/api/system/stop-monitoring")
async def stop_monitoring():
    """Stop real-time monitoring"""
    await websocket_manager.stop_monitoring()
    return {"message": "Monitoring stopped"}

@app.post("/api/system/test-notifications")
async def test_notifications():
    """Test notification system"""
    try:
        await notification_manager.test_notifications()
        return {"message": "Notification test completed successfully"}
    except Exception as e:
        return {"message": f"Notification test failed: {str(e)}"}

@app.get("/api/system/info")
async def system_info():
    """Get system information"""
    return {
        "version": "1.0.0",
        "services": {
            "scheduler_running": scheduler.running,
            "websocket_connections": len(websocket_manager.connections),
            "notification_channels": notification_manager.notification_channels
        }
    }

# Include API routers
app.include_router(pairs_api.router, prefix="/api/v1/pairs", tags=["pairs"])
app.include_router(backtest_api.router, prefix="/api/v1/backtest", tags=["backtest"])
app.include_router(alerts_api.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(market_data_api.router, prefix="/api/v1/market-data", tags=["market-data"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
