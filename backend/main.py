from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from router.router import user
from middleware.error_handler import register_exception_handlers
from config.logger_config import get_api_logger, log_request
from utils.response_models import success_response
import time

# Configurar logger
logger = get_api_logger()

app = FastAPI(
    title="API Usuario FastAPI",
    description="API para gestión de usuarios con carga masiva desde Excel",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Registrar manejadores de excepciones
register_exception_handlers(app)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",      # Angular Frontend
        "http://127.0.0.1:4200",      # Angular Frontend (alternativo)
        "http://localhost:8000",      # Swagger UI
        "http://127.0.0.1:8000",      # Swagger UI (alternativo)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para loguear todos los requests"""
    start_time = time.time()
    
    # Log del request entrante
    logger.info(f"⏩ Incoming: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        
        # Calcular duración
        duration = (time.time() - start_time) * 1000
        
        # Log del response
        log_request(logger, request.method, request.url.path, response.status_code, duration)
        
        return response
    
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        logger.error(
            f"✗ Error procesando request: {request.method} {request.url.path} | "
            f"{duration:.2f}ms | {type(e).__name__}: {str(e)}"
        )
        raise


# Incluir routers
app.include_router(user)


@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("=" * 60)
    logger.info("🚀 Iniciando API Usuario FastAPI")
    logger.info("=" * 60)
    logger.info("✓ Aplicación iniciada correctamente")
    logger.info("📚 Documentación disponible en: /docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    logger.info("=" * 60)
    logger.info("🛑 Deteniendo API Usuario FastAPI")
    logger.info("=" * 60)


@app.get("/", tags=["Root"])
def root():
    """Endpoint raíz de la API"""
    logger.debug("Acceso al endpoint raíz")
    return success_response(
        message="API funcionando correctamente",
        data={
            "version": "1.0.0",
            "service": "usuarios-api",
            "endpoints": {
                "docs": "/docs",
                "usuarios": "/api/user",
                "health": "/health"
            }
        }
    )


@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint para verificar el estado de la API"""
    logger.debug("Health check ejecutado")
    return success_response(
        message="Servicio saludable",
        data={
            "status": "healthy",
            "service": "usuarios-api",
            "version": "1.0.0"
        }
    )