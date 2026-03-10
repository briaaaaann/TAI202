#IMPORTACIONES, LISTAS Y MODELOS
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # CORRECCIÓN AQUÍ
import jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from typing import Literal

app = FastAPI(title="API Adopcion Mascotas")

mascotas = []
adopciones = []

class Mascota(BaseModel):
    id: int = Field(..., gt=0, description="ID Unico")
    nombre: str = Field(..., min_length=2, max_length=50)
    especie: str = Field(..., min_length=2, max_length=50, description="ej. Perro, Gato")
    estado: Literal["Disponible", "Adoptado"] = "Disponible" 

class Adopcion(BaseModel):
    id_adopcion: int = Field(..., gt=0, description="ID Unico")
    id_mascota: int = Field(..., gt=0, description="ID Unico")
    nombre_adoptante: str = Field(..., min_length=2, max_length=50)

SECRET_KEY = "mi_clave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#CONFIGURACION JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # CORRECCIÓN AQUÍ

@app.post("/token", tags=['Seguridad'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "refugio" or form_data.password != "adopta123":
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": form_data.username, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer"}

#Función para verificar el token en las rutas protegidas
async def verificar_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Credenciales invalidas")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado. Inicia sesion nuevamente.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalido")

#RUTAS PÚBLICAS Y PROTEGIDAS 

#Filtra y devuelve solo las disponibles
@app.get("/mascotas/disponibles", tags=['Mascotas'])
async def ver_disponibles():
    disponibles = [mascota for mascota in mascotas if mascota["estado"] == "Disponible"]
    return {"total": len(disponibles), "mascotas": disponibles}

#Agrega una mascota
@app.post("/mascotas/", status_code=status.HTTP_201_CREATED, tags=['Mascotas'])
async def agregar_mascota(mascota: Mascota, usuario_actual: str = Depends(verificar_token)):
    # Verificamos que el ID no exista
    if any(m["id"] == mascota.id for m in mascotas):
        raise HTTPException(status_code=400, detail="ID Existente")
    
    # model_dump() convierte el modelo Pydantic a diccionario
    mascotas.append(mascota.model_dump())
    return {"mensaje": "Mascota registrada exitosamente", "mascota": mascota}

#Registra la adopción y cambia el estado de la mascota
@app.post("/adopciones/", status_code=status.HTTP_201_CREATED, tags=['Adopciones'])
async def registrar_adopcion(adopcion: Adopcion, usuario_actual: str = Depends(verificar_token)):
    # Buscamos la mascota en la lista
    mascota_encontrada = next((m for m in mascotas if m["id"] == adopcion.id_mascota), None)
    
    if not mascota_encontrada:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    
    # Verificamos disponibilidad
    if mascota_encontrada["estado"] == "Adoptado":
        raise HTTPException(status_code=409, detail="La mascota ya fue adoptada")
    
    # Cambiamos el estado y guardamos la adopción
    mascota_encontrada["estado"] = "Adoptado"
    adopciones.append(adopcion.model_dump())
    
    return {"mensaje": "Adopcion registrada exitosamente", "datos": adopcion}