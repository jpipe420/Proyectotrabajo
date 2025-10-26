from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class UsuarioExcel(BaseModel):
    """Modelo para un usuario desde Excel"""
    nombre: str
    username: str
    correo: str
    user_passw: str
    fila_original: Optional[int] = None
    estado_validacion: Optional[str] = 'valido'  # valido, duplicado, error
    mensaje_validacion: Optional[str] = ''

class HojaAnalisis(BaseModel):
    """Modelo para el análisis de una hoja de Excel"""
    nombre_hoja: str
    total_filas: int
    es_valida: bool
    datos: List[Dict[str, Any]] = []
    errores: List[str] = []
    total_validos: Optional[int] = 0
    total_duplicados: Optional[int] = 0

class AnalisisExcelResponse(BaseModel):
    """Respuesta del análisis de Excel"""
    exito: bool
    nombre_archivo: str
    total_hojas: int
    hojas_validas: List[HojaAnalisis]
    hojas_invalidas: List[HojaAnalisis]
    resumen: Dict[str, int]

class ConfirmacionCarga(BaseModel):
    """Modelo para confirmar la carga de usuarios"""
    registros: List[Dict[str, str]]

class ConfirmacionResponse(BaseModel):
    """Respuesta de la confirmación de carga"""
    exito: bool
    mensaje: str
    usuarios_creados: int
    errores: Optional[List[str]] = None
    total_procesados: int

class EstadisticasUsuarios(BaseModel):
    """Modelo para estadísticas de usuarios"""
    total_usuarios: int
    usuarios_por_mes: List[Dict[str, Any]]
    usuarios_por_dominio: List[Dict[str, Any]]
    usuarios_por_dia: List[Dict[str, Any]]