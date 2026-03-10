from fastapi import FastAPI, status, HTTPException, Query, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Literal, Optional, List
from datetime import date, datetime, timedelta, timezone

app = FastAPI(title="API Gestión de Eventos y Conferencias Protegida")

# Base de datos en memoria
eventos = []

# --- CONFIGURACIÓN DE SEGURIDAD JWT ---
SECRET_KEY = "super_secreto_eventos"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token", tags=['Seguridad'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Credenciales de prueba: admin / admin123
    if form_data.username != "admin" or form_data.password != "admin123":
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": form_data.username, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer"}

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

# --- MODELOS PYDANTIC ---

class Evento(BaseModel):
    id: int = Field(..., gt=0, description="ID único del evento")
    titulo: str = Field(..., min_length=5, max_length=100)
    capacidad: int = Field(..., ge=10, le=1000, description="Capacidad entre 10 y 1000")
    fecha: date = Field(..., description="Fecha en formato YYYY-MM-DD")
    email_organizador: EmailStr = Field(..., description="Correo válido del organizador")
    estado: Literal["Programado", "En curso", "Finalizado", "Cancelado"] = "Programado"

    @field_validator('fecha')
    @classmethod
    def validar_fecha_futura(cls, v):
        if v < date.today():
            raise ValueError('La fecha del evento no puede ser en el pasado')
        return v

class EventoUpdate(BaseModel):
    """Modelo para PATCH: Todos los campos son opcionales"""
    titulo: Optional[str] = Field(None, min_length=5, max_length=100)
    capacidad: Optional[int] = Field(None, ge=10, le=1000)
    fecha: Optional[date] = None
    email_organizador: Optional[EmailStr] = None
    estado: Optional[Literal["Programado", "En curso", "Finalizado", "Cancelado"]] = None

    @field_validator('fecha')
    @classmethod
    def validar_fecha_futura(cls, v):
        if v is not None and v < date.today():
            raise ValueError('La fecha del evento no puede ser en el pasado')
        return v


# --- ENDPOINTS ---

# 1. GET (PÚBLICO): Leer todos los eventos 
@app.get("/v1/eventos/", tags=['Eventos'])
async def obtener_eventos(estado: Optional[str] = Query(None, description="Filtrar por estado")):
    if estado:
        filtrados = [e for e in eventos if e["estado"].lower() == estado.lower()]
        return {"total": len(filtrados), "eventos": filtrados}
    return {"total": len(eventos), "eventos": eventos}

# 2. POST (PROTEGIDO): Crear un nuevo evento
@app.post("/v1/eventos/", status_code=status.HTTP_201_CREATED, tags=['Eventos'])
async def crear_evento(evento: Evento, usuario: str = Depends(verificar_token)):
    if any(e["id"] == evento.id for e in eventos):
        raise HTTPException(status_code=400, detail="El ID del evento ya existe")
    
    eventos.append(evento.model_dump())
    return {"mensaje": "Evento creado exitosamente", "evento": evento, "creado_por": usuario}

# 3. PUT (PROTEGIDO): Reemplazo total del recurso
@app.put("/v1/eventos/{evento_id}", tags=['Eventos'])
async def actualizar_evento_completo(evento_id: int, evento_actualizado: Evento, usuario: str = Depends(verificar_token)):
    for indice, evento in enumerate(eventos):
        if evento["id"] == evento_id:
            nuevo_evento = evento_actualizado.model_dump()
            nuevo_evento["id"] = evento_id 
            eventos[indice] = nuevo_evento
            return {"mensaje": "Evento reemplazado (PUT)", "evento": eventos[indice]}
            
    raise HTTPException(status_code=404, detail="Evento no encontrado")

# 4. PATCH (PROTEGIDO): Actualización parcial del recurso
@app.patch("/v1/eventos/{evento_id}", tags=['Eventos'])
async def actualizar_evento_parcial(evento_id: int, evento_update: EventoUpdate, usuario: str = Depends(verificar_token)):
    for evento in eventos:
        if evento["id"] == evento_id:
            datos_a_actualizar = evento_update.model_dump(exclude_unset=True)
            evento.update(datos_a_actualizar)
            return {"mensaje": "Evento actualizado parcialmente (PATCH)", "evento": evento}
            
    raise HTTPException(status_code=404, detail="Evento no encontrado")

# 5. DELETE (PROTEGIDO): Eliminar un evento
@app.delete("/v1/eventos/{evento_id}", tags=['Eventos'])
async def eliminar_evento(evento_id: int, usuario: str = Depends(verificar_token)):
    for i, evento in enumerate(eventos):
        if evento["id"] == evento_id:
            evento_eliminado = eventos.pop(i)
            return {"mensaje": "Evento eliminado correctamente", "evento": evento_eliminado}
            
    raise HTTPException(status_code=404, detail="Evento no encontrado")