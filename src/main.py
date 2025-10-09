"""
BookGen Sistema Automatizado - FastAPI Application
Main entry point for the BookGen API server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from datetime import datetime, timezone

# Import routers
from .api.routers.biographies import router as biographies_router
from .api.routers.sources import router as sources_router
from .api.routers.metrics import router as metrics_router
from .api.routers.websocket import router as websocket_router
from .api.routers.collections import router as collections_router

# Import middleware
from .api.middleware.rate_limiter import RateLimitMiddleware
from .api.middleware.request_logger import RequestLoggerMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="BookGen AI System",
    description="Sistema Automatizado de Generación de Libros con IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
# Request logging middleware
app.add_middleware(RequestLoggerMiddleware)

# Rate limiting middleware (60 requests per minute per IP)
rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=rate_limit_per_minute
)

# Include routers
app.include_router(biographies_router)
app.include_router(sources_router)
app.include_router(metrics_router)
app.include_router(websocket_router)
app.include_router(collections_router)

logger.info("BookGen API server initialized")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "BookGen AI System",
        "version": "1.0.0",
        "status": "running",
        "environment": os.getenv("ENV", "development")
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint para Docker HEALTHCHECK
    Retorna el estado del sistema
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": os.getenv("ENV", "development"),
        "debug": os.getenv("DEBUG", "false").lower() == "true"
    }


@app.get("/api/v1/status")
async def api_status():
    """Status endpoint con información adicional del sistema"""
    return {
        "api_version": "v1",
        "status": "operational",
        "services": {
            "api": "running",
            "worker": "ready"
        },
        "configuration": {
            "chapters": int(os.getenv("CHAPTERS_NUMBER", 20)),
            "total_words": int(os.getenv("TOTAL_WORDS", 51000)),
            "model": os.getenv("OPENROUTER_MODEL", "qwen/qwen2.5-vl-72b-instruct:free")
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
