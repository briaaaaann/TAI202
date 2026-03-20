from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

#1. Definimos la URL de conexion 
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:123456@postgres:5434/DB_miapi"
)

#2. Creamos el motor de conexion
engine = create_engine(DATABASE_URL)

#3. Preparamos el gestionador de sesiones
SessionLocal = sessionmaker(
    autocommit = False, 
    autoflush = False,
    bind = engine
)

#4. Base declarativa del modelo
Base = declarative_base()

#5. Obtener sesiones de cada peticion
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()