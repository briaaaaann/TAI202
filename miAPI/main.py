#Importaciones
from fastapi import FastAPI
from typing import Optional
import asyncio


#Instancia del servidor
app = FastAPI()

#Endpoints
@app.get("/")
async def holamundo():
    return {"mensaje":"Hola mundo FastAPI"}

@app.get("/bienvenido")
async def bienvenido():
    await asyncio.sleep(5)
    return {
        "mensaje":"Bienvenido a FastAPI",
        "estatus":"200"
        }

#Endpoint con Parametros obligatorios
@app.get("/saludo/{nombre}")
async def saludo(nombre: str):
    return{"mensdaje": f"Hola, {nombre}. Este es un parametro obligatorio"}

#Endpoint con Parametros opcionales
@app.get("/busqueda")
async def buscar(q: Optional[str] = None):
    if q:
        return{"resultado" : f"Estas buscando: {q}"}
    else:
        return{"resultado" : "No buscaste nada"}

