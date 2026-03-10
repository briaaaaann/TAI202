from fastapi import FastAPI, status, HTTPException, Query, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Literal, Optional, List
from datetime import date, datetime, timedelta, timezone

app = FastAPI(title="API Gestión de Proyectos")

reservas = []

class Reserva(BaseModel):
    estado:Optional[Literal["Confirmado", "Espera de confirmacion", "Cancelada"]]

class ReservaUpdate(BaseModel):
    id:int = Field(..., descripcion="ID unico de reserva")
    nombre_cliente:str = Field(..., min_length=6)
    fecha_reserva:date = Field(..., description="Fecha en formato YYYY-MM-DD")
    numero_personas:int = Field(..., ge=1, le=10)
    estado:Literal["Confirmado", "Espera de confirmacion", "Cancelada"] = "Espera de confirmacion"

SECRET_KEY = "clave_secreta"
ALGORITHM = "HS256"
ACCES_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="toekn")

@app.post("/token", tags=['Seguridad'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or form_data.password != "rest123":
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCES_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": form_data.username, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_toeken": token, "token_type": "bearer"}

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

def validar_fecha(cls, v):
    if v < date.today():
        raise ValueError('La fehca de la reserva tiene que ser fututa')
    return v

@app.get("/reservas", tags=['Reservas'])
async def listar_Reservas():
    return{"total": len(reservas), "Reservas": reservas}

@app.post("/reservas/{id_reserva}", status_code=status.HTTP_201_CREATED, tags=['Reservas'])
async def crear_reserva(reserva:Reserva):
    if any(e["id"] == reserva.id for e in reservas):
        raise HTTPException(status_code=400, detail="El ID de la reserva la existe")
    reservas.append(reserva.model_dump())
    return{"mensaje": "Reserva creada exitosamente", "reserva": reserva}

@app.get("/reservas/{id_reserva}", tags=['Reservas'])
async def listar_ReservasID(id_reserva: int):
    for i, reserva in enumerate(reservas):
        if reserva["id"] == id_reserva:
            return{"reserva": reserva}
        
@app.patch("/confirmar_reserva/{id_reserva}", tags=['Reservas'])
async def confirmar_reserva(id_reserva: int, reserva_update: ReservaUpdate):
    for reserva in reservas:
        if reserva["id"] == id_reserva:
            cambio_estado = reserva_update.model_dump(exclude_unset=True)
            reserva.update(cambio_estado)
            return{"mensaje": "Reserva confirmada", "reserva": reserva}
        raise HTTPException(status_code=404, details="Reserva no encontrada")
    
@app.patch("/cancelar_reserva/{id_reserva}", tags=['Reservas'])
async def cancelar_reserva(id_reserva: int, reserva_update: ReservaUpdate):
    for reserva in reservas:
        if reserva["id"] == id_reserva:
            cambio_estado = reserva_update.model_dump(exclude_unset=True)
            reserva.update(cambio_estado)
            return{"mensaje": "Reserva cancelada", "reserva": reserva}
        raise HTTPException(status_code=404, details="Reserva no encontrada")
    
#Ejemplo JSON

{
    "id" : 1,
    "nombre_cliente" : "Santiago Camacho",
    "fecha_reserva" : "2026-10-03",
    "numero_personas" : 5,
    "estado" : "Confirmado"
}

{
    "estado" : "Confirmado"
}