import asyncio
from typing import Optional
from app.data.database import usuarios
from fastapi import APIRouter

# DECLARACIÓN DE ROUTER
misc = APIRouter(tags = ["Varios"])

# Endpoints
@misc.get("/")
async def holaMundo():
    return {"mensaje":"Hola Mundo FastAPI"}

@misc.get("/bienvenido")
async def bienvenido():
    await asyncio.sleep(5)
    return {
        "mensaje":"Bienvenido a FastAPI",
        "estatus":200
    }

# Enpoint con parámetros obligatorios
@misc.get("/v1/parametroObligatorio/{id}")
async def consulta_uno(id: int):
    return {"mensaje":"Usuario encontrado",
            "usuario":id,
            "status":200}

# Endpoint con parámetros opcionales
@misc.get("/v1/parametroOpcional/")
async def consulta_todos(id:Optional[int] = None):
    if id is not None:
        for usuarioK in usuarios:
            if usuarioK["id"] == id:
                return {"mensaje":"Usuario encontrado", "usuario":usuarioK}
        return {"mensaje":"Usuario no encontrado", "status":200}
    else:
        return {"mensaje":"No se proporcionó ID.", "status":200}