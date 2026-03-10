from fastapi import FastAPI, status, HTTPException, Query
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Literal, Optional, List
from datetime import date

app = FastAPI(title="API Gestión de Eventos y Conferencias")

# Base de datos en memoria
eventos = []

# MODELOS PYDANTIC 

class Evento(BaseModel):
    id: int = Field(..., gt=0, description="ID único del evento")
    titulo: str = Field(..., min_length=5, max_length=100)
    capacidad: int = Field(..., ge=10, le=1000, description="Capacidad entre 10 y 1000")
    fecha: date = Field(..., description="Fecha en formato YYYY-MM-DD")
    email_organizador: EmailStr = Field(..., description="Correo válido del organizador")
    estado: Literal["Programado", "En curso", "Finalizado", "Cancelado"] = "Programado"

    # Validador personalizado para asegurar que la fecha no sea en el pasado
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


# ENDPOINTS 

# 1. GET: Leer todos los eventos (con filtro opcional por estado)
@app.get("/v1/eventos/", tags=['Eventos'])
async def obtener_eventos(estado: Optional[str] = Query(None, description="Filtrar por estado")):
    if estado:
        filtrados = [e for e in eventos if e["estado"].lower() == estado.lower()]
        return {"total": len(filtrados), "eventos": filtrados}
    return {"total": len(eventos), "eventos": eventos}

# 2. POST: Crear un nuevo evento
@app.post("/v1/eventos/", status_code=status.HTTP_201_CREATED, tags=['Eventos'])
async def crear_evento(evento: Evento):
    if any(e["id"] == evento.id for e in eventos):
        raise HTTPException(status_code=400, detail="El ID del evento ya existe")
    
    eventos.append(evento.model_dump())
    return {"mensaje": "Evento creado exitosamente", "evento": evento}

# 3. PUT: Reemplazo total del recurso

@app.put("/v1/eventos/{evento_id}", tags=['Eventos'])
async def actualizar_evento_completo(evento_id: int, evento_actualizado: Evento):
    """PUT requiere que envíes TODOS los campos del modelo para reemplazar el existente."""
    for indice, evento in enumerate(eventos):
        if evento["id"] == evento_id:
            # Reemplazamos el diccionario completo, pero mantenemos el ID original por seguridad
            nuevo_evento = evento_actualizado.model_dump()
            nuevo_evento["id"] = evento_id 
            eventos[indice] = nuevo_evento
            return {"mensaje": "Evento reemplazado (PUT)", "evento": eventos[indice]}
            
    raise HTTPException(status_code=404, detail="Evento no encontrado")

# 4. PATCH: Actualización parcial del recurso
@app.patch("/v1/eventos/{evento_id}", tags=['Eventos'])
async def actualizar_evento_parcial(evento_id: int, evento_update: EventoUpdate):
    """PATCH permite enviar solo los campos que quieres modificar."""
    for evento in eventos:
        if evento["id"] == evento_id:
            # exclude_unset=True extrae SOLO los campos que el usuario envió en el JSON
            datos_a_actualizar = evento_update.model_dump(exclude_unset=True)
            
            # Actualizamos el diccionario original con los nuevos datos
            evento.update(datos_a_actualizar)
            return {"mensaje": "Evento actualizado parcialmente (PATCH)", "evento": evento}
            
    raise HTTPException(status_code=404, detail="Evento no encontrado")

# 5. DELETE: Eliminar un evento
@app.delete("/v1/eventos/{evento_id}", tags=['Eventos'])
async def eliminar_evento(evento_id: int):
    for i, evento in enumerate(eventos):
        if evento["id"] == evento_id:
            evento_eliminado = eventos.pop(i)
            return {"mensaje": "Evento eliminado correctamente", "evento": evento_eliminado}
            
    raise HTTPException(status_code=404, detail="Evento no encontrado")