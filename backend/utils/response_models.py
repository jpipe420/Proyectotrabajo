from typing import Optional, Any, Dict, List, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# TypeVar para respuestas genéricas
T = TypeVar('T')


class StatusEnum(str, Enum):
    """Estados posibles de las respuestas"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ResponseMetadata(BaseModel):
    """Metadata adicional para las respuestas"""
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"
    request_id: Optional[str] = None
    execution_time_ms: Optional[float] = None


class StandardResponse(BaseModel, Generic[T]):
    """
    Respuesta estándar para todos los endpoints
    
    Estructura unificada:
    {
        "status": "success|error|warning|info",
        "message": "Mensaje descriptivo",
        "data": { ... datos ... },
        "errors": [ ... errores ... ],
        "metadata": { ... información adicional ... }
    }
    """
    status: StatusEnum
    message: str
    data: Optional[T] = None
    errors: Optional[List[str]] = None
    metadata: Optional[ResponseMetadata] = Field(default_factory=ResponseMetadata)
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Operación exitosa",
                "data": {"id": 1, "nombre": "Usuario"},
                "errors": None,
                "metadata": {
                    "timestamp": "2024-01-01T12:00:00",
                    "version": "1.0.0"
                }
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Respuesta para endpoints paginados"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==========================================
# FUNCIONES HELPER PARA CREAR RESPUESTAS
# ==========================================

def success_response(
    message: str,
    data: Any = None,
    metadata: Optional[Dict] = None
) -> Dict:
    """
    Crea una respuesta exitosa estandarizada
    
    Args:
        message: Mensaje descriptivo
        data: Datos de respuesta
        metadata: Metadata adicional
    
    Returns:
        Diccionario con la respuesta estándar
    """
    response_metadata = ResponseMetadata(**(metadata or {}))
    
    return {
        "status": StatusEnum.SUCCESS,
        "message": message,
        "data": data,
        "errors": None,
        "metadata": response_metadata.model_dump()
    }


def error_response(
    message: str,
    errors: List[str] = None,
    data: Any = None,
    metadata: Optional[Dict] = None
) -> Dict:
    """
    Crea una respuesta de error estandarizada
    
    Args:
        message: Mensaje de error principal
        errors: Lista de errores específicos
        data: Datos adicionales (opcional)
        metadata: Metadata adicional
    
    Returns:
        Diccionario con la respuesta de error
    """
    response_metadata = ResponseMetadata(**(metadata or {}))
    
    return {
        "status": StatusEnum.ERROR,
        "message": message,
        "data": data,
        "errors": errors or [],
        "metadata": response_metadata.model_dump()
    }


def warning_response(
    message: str,
    data: Any = None,
    warnings: List[str] = None,
    metadata: Optional[Dict] = None
) -> Dict:
    """
    Crea una respuesta de advertencia
    
    Args:
        message: Mensaje de advertencia
        data: Datos de respuesta
        warnings: Lista de advertencias
        metadata: Metadata adicional
    
    Returns:
        Diccionario con la respuesta de advertencia
    """
    response_metadata = ResponseMetadata(**(metadata or {}))
    
    return {
        "status": StatusEnum.WARNING,
        "message": message,
        "data": data,
        "errors": warnings or [],
        "metadata": response_metadata.model_dump()
    }


def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "Datos obtenidos exitosamente",
    metadata: Optional[Dict] = None
) -> Dict:
    """
    Crea una respuesta paginada
    
    Args:
        items: Lista de items
        total: Total de registros
        page: Página actual
        page_size: Tamaño de página
        message: Mensaje descriptivo
        metadata: Metadata adicional
    
    Returns:
        Diccionario con respuesta paginada
    """
    import math
    
    total_pages = math.ceil(total / page_size) if page_size > 0 else 0
    
    pagination_data = {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    
    return success_response(
        message=message,
        data=pagination_data,
        metadata=metadata
    )


# ==========================================
# MODELOS ESPECÍFICOS DE RESPUESTA
# ==========================================

class UserResponse(BaseModel):
    """Respuesta para endpoints de usuarios"""
    id: int
    nombre: str
    username: str
    correo: str
    created_at: Optional[datetime] = None


class ExcelAnalysisResponse(BaseModel):
    """Respuesta para análisis de Excel"""
    nombre_archivo: str
    total_hojas: int
    hojas_validas: List[Dict]
    hojas_invalidas: List[Dict]
    resumen: Dict


class ConfirmUploadResponse(BaseModel):
    """Respuesta para confirmación de carga"""
    usuarios_creados: int
    total_procesados: int
    errores: Optional[List[str]] = None


class StatisticsResponse(BaseModel):
    """Respuesta para estadísticas"""
    total_usuarios: int
    resumen_temporal: Dict
    usuarios_por_mes: List[Dict]
    usuarios_por_dominio: List[Dict]


# ==========================================
# EXCEPCIONES PERSONALIZADAS
# ==========================================

class BusinessException(Exception):
    """Excepción base para errores de negocio"""
    def __init__(
        self, 
        message: str, 
        status_code: int = 400,
        errors: List[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(self.message)


class ValidationException(BusinessException):
    """Excepción para errores de validación"""
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message, status_code=422, errors=errors)


class NotFoundException(BusinessException):
    """Excepción para recursos no encontrados"""
    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message, status_code=404)


class DuplicateException(BusinessException):
    """Excepción para duplicados"""
    def __init__(self, message: str = "El registro ya existe"):
        super().__init__(message, status_code=409)


class UnauthorizedException(BusinessException):
    """Excepción para acceso no autorizado"""
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, status_code=401)