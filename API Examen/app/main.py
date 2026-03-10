from fastapi import FastAPI, status, HTTPException, Query, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Literal, Optional, List
from datetime import date, datetime, timedelta, timezone

app = FastAPI(title="API Gestión de Proyectos")

reservas = []

class Reserva(BaseModel):
    id:int = Field(..., descripcion="ID unico de reserva")
    nombre_cliente:str = Field(..., min_length=6)
    fecha_reserva:date = Field(..., description="Fecha en formato YYYY-MM-DD")
    numero_personas:int = Field(..., ge=1, le=10)
    estado:Literal["Confirmado", "Espera de confirmacion", "Cancelada"]

def validar_fecha(cls, v):
    if v < date.today():
        raise ValueError('La fehca de la reserva tiene que ser fututa')
    return v

@app.get("/reservas", tags=['Reservas'])
async def listar_Reservas():
    return{"total": len(reservas), "Reservas": reservas}

@app.post("/reserva/{reserva_id}", status_code=status.HTTP_201_CREATED, tags=['Reservas'])
async def crear_reserva(reserva:Reserva):
    if any(e["id"] == reserva.id for e in reservas):
        raise HTTPException(status_code=400, detail="El ID de la reserva la existe")
    reservas.append(reserva.model_dump())
    return{"mensaje": "Reserva creada exitosamente", "reserva": reserva}

@app.get("/reservas", tags=['Reservas'])
async def listar_ReservasID(id_reserva: Optional[int] = Query(None, description="Filtrar por ID: ")):
    if id_reserva:
        filtro = [e for e in reservas id_reserva == id]
        return