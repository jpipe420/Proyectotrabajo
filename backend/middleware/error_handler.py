from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from utils.response_models import (
    error_response,
    BusinessException,
    ValidationException,
    NotFoundException,
    DuplicateException,
    UnauthorizedException
)
from config.logger_config import get_error_logger
import traceback

logger = get_error_logger()


async def business_exception_handler(request: Request, exc: BusinessException):
    """Manejador para excepciones de negocio personalizadas"""
    logger.warning(
        f"Business Exception | {exc.status_code} | {request.method} {request.url.path} | {exc.message}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.message,
            errors=exc.errors,
            metadata={
                "path": str(request.url.path),
                "method": request.method
            }
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejador para errores de validación de Pydantic"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append(f"{field}: {error['msg']}")
    
    logger.warning(
        f"Validation Error | {request.method} {request.url.path} | Errors: {len(errors)}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            message="Error de validación en los datos enviados",
            errors=errors,
            metadata={
                "path": str(request.url.path),
                "method": request.method
            }
        )
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Manejador para excepciones HTTP estándar"""
    logger.warning(
        f"HTTP Exception | {exc.status_code} | {request.method} {request.url.path} | {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.detail,
            metadata={
                "path": str(request.url.path),
                "method": request.method
            }
        )
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Manejador para errores de SQLAlchemy"""
    
    # Error de integridad (duplicados, FK, etc)
    if isinstance(exc, IntegrityError):
        error_msg = str(exc.orig)
        
        # Detectar tipo de error
        if "Duplicate entry" in error_msg:
            message = "El registro ya existe en la base de datos"
            if "username" in error_msg:
                message = "El username ya está registrado"
            elif "correo" in error_msg:
                message = "El correo ya está registrado"
        elif "foreign key constraint" in error_msg.lower():
            message = "Error de integridad: referencia a un registro inexistente"
        else:
            message = "Error de integridad en la base de datos"
        
        logger.error(
            f"Integrity Error | {request.method} {request.url.path} | {error_msg}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=error_response(
                message=message,
                errors=[error_msg],
                metadata={
                    "path": str(request.url.path),
                    "method": request.method
                }
            )
        )
    
    # Otros errores de BD
    logger.error(
        f"Database Error | {request.method} {request.url.path} | {str(exc)}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            message="Error en la base de datos",
            errors=[str(exc)],
            metadata={
                "path": str(request.url.path),
                "method": request.method
            }
        )
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Manejador para excepciones no capturadas"""
    
    # Log del error completo con traceback
    error_traceback = traceback.format_exc()
    logger.critical(
        f"Unhandled Exception | {request.method} {request.url.path}\n"
        f"Type: {type(exc).__name__}\n"
        f"Message: {str(exc)}\n"
        f"Traceback:\n{error_traceback}"
    )
    
    # En producción, no revelar detalles del error
    import os
    is_production = os.getenv("ENVIRONMENT", "development") == "production"
    
    if is_production:
        message = "Error interno del servidor"
        errors = None
    else:
        message = f"Error no controlado: {type(exc).__name__}"
        errors = [str(exc), error_traceback[:500]]  # Limitar traceback
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            message=message,
            errors=errors,
            metadata={
                "path": str(request.url.path),
                "method": request.method,
                "error_type": type(exc).__name__
            }
        )
    )


# Función para registrar todos los manejadores
def register_exception_handlers(app):
    """
    Registra todos los manejadores de excepciones en la app
    
    Usage en main.py:
        from middleware.error_handler import register_exception_handlers
        register_exception_handlers(app)
    """
    
    # Excepciones personalizadas
    app.add_exception_handler(BusinessException, business_exception_handler)
    app.add_exception_handler(ValidationException, business_exception_handler)
    app.add_exception_handler(NotFoundException, business_exception_handler)
    app.add_exception_handler(DuplicateException, business_exception_handler)
    app.add_exception_handler(UnauthorizedException, business_exception_handler)
    
    # Excepciones de FastAPI/Starlette
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Excepciones de base de datos
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    # Catch-all para excepciones no manejadas
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("✓ Manejadores de excepciones registrados")