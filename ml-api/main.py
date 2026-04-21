"""
FastAPI Application - Sistema de Análisis Académico
Punto de entrada principal de la API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from app.config import settings
from app.api import prediccion, reportes, recomendaciones
from app.utils.logger import setup_logging

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación
    Inicialización y limpieza de recursos
    """
    # Startup
    logger.info("🚀 Iniciando Sistema de Análisis Académico - ML API")
    logger.info(f"📊 Versión: {settings.api_version}")
    logger.info(f"🔗 Supabase URL: {settings.supabase_url}")
    
    # Crear directorios necesarios
    import os
    os.makedirs(settings.model_path, exist_ok=True)
    os.makedirs(settings.reports_output_dir, exist_ok=True)
    logger.info("✅ Directorios creados correctamente")
    
    yield
    
    # Shutdown
    logger.info("👋 Cerrando aplicación...")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================
# RUTAS PRINCIPALES
# ================================================

@app.get("/")
async def root():
    """Endpoint raíz - Información de la API"""
    return {
        "message": "Sistema Inteligente de Análisis del Rendimiento Académico",
        "institution": "IE Pública Dos de Mayo - Chincha",
        "version": settings.api_version,
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "predicciones": "/api/prediccion",
            "recomendaciones": "/api/recomendaciones",
            "reportes": "/api/reportes"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Verificar conexión a Supabase (básico)
        from app.utils.supabase_client import get_supabase_client
        client = get_supabase_client()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "supabase": "connected",
            "ml_models": "ok"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


# ================================================
# INCLUIR ROUTERS
# ================================================

app.include_router(
    prediccion.router,
    prefix="/api/prediccion",
    tags=["Predicciones ML"]
)

app.include_router(
    recomendaciones.router,
    prefix="/api/recomendaciones",
    tags=["Recomendaciones Pedagógicas"]
)

app.include_router(
    reportes.router,
    prefix="/api/reportes",
    tags=["Reportes y Documentos"]
)


# ================================================
# MANEJADORES DE ERRORES
# ================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Manejador personalizado de excepciones HTTP"""
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Manejador general de excepciones"""
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# ================================================
# ENTRY POINT
# ================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        workers=settings.api_workers,
        log_level=settings.log_level.lower()
    )
