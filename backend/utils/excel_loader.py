import pandas as pd
from typing import List, Dict, Tuple, Optional
import os

class ExcelLoader:
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    REQUIRED_COLUMNS = ['nombre', 'username', 'correo', 'user_passw']
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Verifica si el archivo tiene extensión permitida"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ExcelLoader.ALLOWED_EXTENSIONS
    
    @staticmethod
    def get_sheet_info(file_path: str) -> Tuple[bool, Dict, str]:
        """
        Obtiene información sobre las hojas del archivo Excel
        
        Returns:
            Tuple con (es_exitoso, info_hojas, mensaje)
            info_hojas contiene: {
                'total_sheets': int,
                'sheet_names': List[str],
                'rows_per_sheet': Dict[str, int]
            }
        """
        try:
            # Leer todas las hojas
            excel_file = pd.ExcelFile(file_path)
            
            info = {
                'total_sheets': len(excel_file.sheet_names),
                'sheet_names': excel_file.sheet_names,
                'rows_per_sheet': {}
            }
            
            # Contar filas por hoja
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                info['rows_per_sheet'][sheet_name] = len(df)
            
            mensaje = f"Archivo con {info['total_sheets']} hoja(s): {', '.join(info['sheet_names'])}"
            return True, info, mensaje
            
        except Exception as e:
            return False, {}, f"Error al leer información de hojas: {str(e)}"
    
    @staticmethod
    def read_excel(file_path: str, sheet_name: Optional[str] = None, validate_single_sheet: bool = True) -> Tuple[bool, List[Dict], str]:
        """
        Lee el archivo Excel y valida los datos
        
        Args:
            file_path: Ruta al archivo Excel
            sheet_name: Nombre de la hoja específica a leer (None = primera hoja)
            validate_single_sheet: Si True, valida que solo haya una hoja
        
        Returns:
            Tuple con (es_valido, datos, mensaje_error)
        """
        try:
            # Primero obtener información de las hojas
            success, sheet_info, msg = ExcelLoader.get_sheet_info(file_path)
            
            if not success:
                return False, [], msg
            
            # Validar número de hojas si se requiere
            if validate_single_sheet and sheet_info['total_sheets'] > 1:
                return False, [], (
                    f"El archivo contiene {sheet_info['total_sheets']} hojas. "
                    f"Solo se permite un archivo con una hoja. "
                    f"Hojas encontradas: {', '.join(sheet_info['sheet_names'])}"
                )
            
            # Leer el archivo Excel
            if sheet_name:
                if sheet_name not in sheet_info['sheet_names']:
                    return False, [], f"La hoja '{sheet_name}' no existe en el archivo"
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                # Leer la primera hoja
                df = pd.read_excel(file_path, sheet_name=0)
            
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
            
            mensaje = f"Archivo válido con {len(datos)} registro(s) desde hoja '{sheet_info['sheet_names'][0] if not sheet_name else sheet_name}'"
            return True, datos, mensaje
            
        except Exception as e:
            return False, [], f"Error al leer el archivo: {str(e)}"
    
    @staticmethod
    def read_excel_all_sheets(file_path: str) -> Tuple[bool, Dict[str, List[Dict]], str]:
        """
        Lee todas las hojas del archivo Excel
        
        Returns:
            Tuple con (es_valido, datos_por_hoja, mensaje)
            datos_por_hoja es un Dict donde la clave es el nombre de la hoja
        """
        try:
            success, sheet_info, msg = ExcelLoader.get_sheet_info(file_path)
            
            if not success:
                return False, {}, msg
            
            datos_por_hoja = {}
            errores_generales = []
            
            for sheet_name in sheet_info['sheet_names']:
                success, datos, mensaje = ExcelLoader.read_excel(
                    file_path, 
                    sheet_name=sheet_name,
                    validate_single_sheet=False
                )
                
                if success:
                    datos_por_hoja[sheet_name] = datos
                else:
                    errores_generales.append(f"Hoja '{sheet_name}': {mensaje}")
            
            if errores_generales:
                return False, {}, "; ".join(errores_generales)
            
            total_registros = sum(len(datos) for datos in datos_por_hoja.values())
            mensaje = f"Se leyeron {total_registros} registros de {len(datos_por_hoja)} hoja(s)"
            
            return True, datos_por_hoja, mensaje
            
        except Exception as e:
            return False, {}, f"Error al leer todas las hojas: {str(e)}"
    
    @staticmethod
    def _validar_datos(datos: List[Dict]) -> List[str]:
        """Valida cada registro de datos"""
        errores = []
        usernames_vistos = set()
        correos_vistos = set()
        
        for idx, row in enumerate(datos, 1):
            # Validar email
            correo = str(row.get('correo', '')).strip()
            if not ExcelLoader._es_email_valido(correo):
                errores.append(f"Fila {idx}: Email inválido ({correo})")
            
            # Validar duplicados de correo en el mismo archivo
            if correo in correos_vistos:
                errores.append(f"Fila {idx}: Email duplicado ({correo})")
            correos_vistos.add(correo)
            
            # Validar que no esté vacío
            nombre = str(row.get('nombre', '')).strip()
            if not nombre:
                errores.append(f"Fila {idx}: Nombre vacío")
            
            username = str(row.get('username', '')).strip()
            if not username:
                errores.append(f"Fila {idx}: Username vacío")
            
            # Validar duplicados de username en el mismo archivo
            if username in usernames_vistos:
                errores.append(f"Fila {idx}: Username duplicado ({username})")
            usernames_vistos.add(username)
            
            password = str(row.get('user_passw', '')).strip()
            if not password:
                errores.append(f"Fila {idx}: Contraseña vacía")
            
            if len(username) < 3:
                errores.append(f"Fila {idx}: Username debe tener al menos 3 caracteres")
            
            if len(password) < 6:
                errores.append(f"Fila {idx}: Contraseña debe tener al menos 6 caracteres")
        
        return errores[:10]  # Retorna máximo 10 errores
    
    @staticmethod
    def _es_email_valido(email: str) -> bool:
        """Validación básica de email"""
        import re
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email.strip()) is not None