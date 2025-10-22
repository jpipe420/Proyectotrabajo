from sqlalchemy import create_engine, MetaData
import os
import time  # Necesario para la espera (sleep)
import sys   # Necesario para terminar la aplicación si falla
from sqlalchemy.exc import OperationalError # Importar el tipo de error específico

# --- CONFIGURACIÓN DE RETRIES ---
MAX_RETRIES = 15
RETRY_DELAY = 3  # Esperar 3 segundos entre intentos

# --- OBTENER VARIABLES DE ENTORNO ---
# Nota: La prioridad la tiene el docker-compose.yml, aquí definimos los valores de fallback.
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rootpassword")
DB_HOST = os.getenv("DB_HOST", "db")        # <-- Asegura que el fallback sea 'db'
DB_PORT = os.getenv("DB_PORT", "3306")      # <-- Asegura el puerto interno 3306
DB_NAME = os.getenv("DB_NAME", "dbcrub")

# --- CONSTRUIR LA URL DE CONEXIÓN ---
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# --- LÓGICA DE CONEXIÓN CON REINTENTOS ---
engine = None  # Inicializamos la variable engine
meta_data = MetaData()

for i in range(MAX_RETRIES):
    try:
        print(f"Intento {i+1}/{MAX_RETRIES}: Conectando a la base de datos en {DB_HOST}:{DB_PORT}")
        
        # 1. Crea el motor de conexión
        test_engine = create_engine(DATABASE_URL, echo=True) 
        
        # 2. Intenta hacer una conexión de prueba
        with test_engine.connect():
            engine = test_engine # Si la conexión fue exitosa, asignamos el motor
            print("¡Conexión exitosa a la base de datos!")
            break # Sale del bucle

    except OperationalError as e:
        if i < MAX_RETRIES - 1:
            print(f"Error de conexión: {e}. Esperando {RETRY_DELAY} segundos antes de reintentar...")
            time.sleep(RETRY_DELAY)
        else:
            print("Fallo la conexión después de varios intentos. Verifique que el servicio 'db' esté activo.")
            sys.exit(1) # Detiene la aplicación si falla al final
            
    except Exception as e:
        print(f"Ocurrió un error inesperado al conectar: {e}")
        sys.exit(1)