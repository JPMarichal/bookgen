"""
BookGen Sistema Automatizado - FastAPI Application
Main entry point for the BookGen API server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

# Crear aplicación FastAPI
app = FastAPI(
    title="BookGen AI System",
    description="Sistema Automatizado de Generación de Libros con IA",
    version="1.0.0"
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
        "timestamp": datetime.utcnow().isoformat(),
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
