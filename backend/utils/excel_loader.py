import pandas as pd
from typing import List, Dict, Tuple
import os

class ExcelLoader:
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    REQUIRED_COLUMNS = ['nombre', 'username', 'correo', 'user_passw']
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Verifica si el archivo tiene extensión permitida"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ExcelLoader.ALLOWED_EXTENSIONS
    
    @staticmethod
    def read_excel(file_path: str) -> Tuple[bool, List[Dict], str]:
        """
        Lee el archivo Excel y valida los datos
        
        Returns:
            Tuple con (es_valido, datos, mensaje_error)
        """
        try:
            # Leer el archivo Excel
            df = pd.read_excel(file_path)
            
            # Convertir nombres de columnas a minúsculas
            df.columns = df.columns.str.lower().str.strip()
            
            # Verificar que existan las columnas requeridas
            columnas_faltantes = [col for col in ExcelLoader.REQUIRED_COLUMNS if col not in df.columns]
            if columnas_faltantes:
                return False, [], f"Columnas faltantes: {', '.join(columnas_faltantes)}"
            
            # Validar que no haya filas vacías
            df = df.dropna(subset=ExcelLoader.REQUIRED_COLUMNS, how='any')
            
            if df.empty:
                return False, [], "El archivo Excel no contiene datos válidos"
            
            # Convertir a diccionarios
            datos = df[ExcelLoader.REQUIRED_COLUMNS].to_dict('records')
            
            # Validaciones adicionales
            errores = ExcelLoader._validar_datos(datos)
            if errores:
                return False, [], f"Errores en los datos: {'; '.join(errores)}"
            
            return True, datos, "Archivo válido"
            
        except Exception as e:
            return False, [], f"Error al leer el archivo: {str(e)}"
    
    @staticmethod
    def _validar_datos(datos: List[Dict]) -> List[str]:
        """Valida cada registro de datos"""
        errores = []
        
        for idx, row in enumerate(datos, 1):
            # Validar email
            if not ExcelLoader._es_email_valido(row.get('correo', '')):
                errores.append(f"Fila {idx}: Email inválido ({row.get('correo')})")
            
            # Validar que no esté vacío
            if not row.get('nombre', '').strip():
                errores.append(f"Fila {idx}: Nombre vacío")
            
            if not row.get('username', '').strip():
                errores.append(f"Fila {idx}: Username vacío")
            
            if not row.get('user_passw', '').strip():
                errores.append(f"Fila {idx}: Contraseña vacía")
            
            if len(row.get('username', '')) < 3:
                errores.append(f"Fila {idx}: Username debe tener al menos 3 caracteres")
        
        return errores[:5]  # Retorna máximo 5 errores
    
    @staticmethod
    def _es_email_valido(email: str) -> bool:
        """Validación básica de email"""
        import re
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email.strip()) is not None