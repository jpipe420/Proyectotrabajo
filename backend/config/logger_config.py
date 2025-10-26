import logging
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
import os

# Crear directorio de logs si no existe
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Configuración de niveles de log
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Formato personalizado para los logs
LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | "
    "%(funcName)s:%(lineno)d | %(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Colores para logs en consola (solo en desarrollo)
class ColoredFormatter(logging.Formatter):
    """Formatter con colores para mejor lectura en consola"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarillo
        'ERROR': '\033[31m',      # Rojo
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(name: str, log_file: str = None, level: str = LOG_LEVEL) -> logging.Logger:
    """
    Configura y retorna un logger personalizado
    
    Args:
        name: Nombre del logger (usualmente __name__)
        log_file: Nombre del archivo de log (opcional)
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evitar duplicados
    if logger.handlers:
        return logger
    
    # Handler para consola (con colores)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = ColoredFormatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (si se especifica)
    if log_file:
        file_path = LOGS_DIR / log_file
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=10_485_760,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Loggers predefinidos para diferentes módulos
def get_api_logger() -> logging.Logger:
    """Logger para endpoints de la API"""
    return setup_logger("api", "api.log")


def get_database_logger() -> logging.Logger:
    """Logger para operaciones de base de datos"""
    return setup_logger("database", "database.log")


def get_excel_logger() -> logging.Logger:
    """Logger para operaciones de Excel"""
    return setup_logger("excel", "excel.log")


def get_auth_logger() -> logging.Logger:
    """Logger para autenticación"""
    return setup_logger("auth", "auth.log")


def get_error_logger() -> logging.Logger:
    """Logger para errores críticos"""
    return setup_logger("error", "error.log", level="ERROR")


# Logger general de la aplicación
app_logger = setup_logger("app", "app.log")


# Función helper para log de requests HTTP
def log_request(logger: logging.Logger, method: str, path: str, status: int, duration: float = None):
    """
    Log estructurado para requests HTTP
    
    Args:
        logger: Logger a usar
        method: Método HTTP (GET, POST, etc)
        path: Ruta del endpoint
        status: Código de estado HTTP
        duration: Duración del request en ms (opcional)
    """
    duration_str = f" | {duration:.2f}ms" if duration else ""
    log_msg = f"{method} {path} | Status: {status}{duration_str}"
    
    if 200 <= status < 300:
        logger.info(log_msg)
    elif 400 <= status < 500:
        logger.warning(log_msg)
    else:
        logger.error(log_msg)


# Función helper para log de operaciones de BD
def log_db_operation(logger: logging.Logger, operation: str, table: str, success: bool, details: str = ""):
    """
    Log estructurado para operaciones de base de datos
    
    Args:
        logger: Logger a usar
        operation: Tipo de operación (SELECT, INSERT, UPDATE, DELETE)
        table: Tabla afectada
        success: Si la operación fue exitosa
        details: Detalles adicionales
    """
    status = "✓" if success else "✗"
    log_msg = f"{status} {operation} | Table: {table}"
    if details:
        log_msg += f" | {details}"
    
    if success:
        logger.info(log_msg)
    else:
        logger.error(log_msg)


# Decorador para log automático de funciones
def log_execution(logger: logging.Logger = None):
    """
    Decorador para loguear ejecución de funciones
    
    Usage:
        @log_execution(get_api_logger())
        def mi_funcion():
            pass
    """
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or app_logger
            func_name = func.__name__
            
            _logger.debug(f" Iniciando ejecución: {func_name}")
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                _logger.debug(f"✓ Completado: {func_name} | {duration:.2f}ms")
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                _logger.error(
                    f"✗ Error en {func_name} | {duration:.2f}ms | {type(e).__name__}: {str(e)}"
                )
                raise
        
        return wrapper
    return decorator