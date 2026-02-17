from fastapi import FastAPI, status, HTTPException
from typing import Optional 
import asyncio

app = FastAPI()

usuarios = [
    {"id": 1, "nombre": "Santiago", "edad": 21},
    {"id": 2, "nombre": "Sergio", "edad": 22},
    {"id": 3, "nombre": "Rodrigo", "edad": 20},
]

@app.get("/v1/usuarios/", tags=['HTTP CRUD'])
async def leer_usuarios():
    return {"total": len(usuarios), "usuarios": usuarios}

@app.post("/v1/usuarios/", tags=['HTTP CRUD'], status_code=status.HTTP_201_CREATED)
async def agregar_usuarios(usuario: dict):
    if any(usr["id"] == usuario.get("id") for usr in usuarios):
        raise HTTPException(status_code=400, detail="El id ya existe")
    
    usuarios.append(usuario)
    return {"mensaje": "Usuario Creado", "datos": usuario}

#NUEVAS RUTAS: PUT, PATCH Y DELETE 
@app.put("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD'])
async def actualizar_usuario_completo(usuario_id: int, usuario_actualizado: dict):
    for indice, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuarios[indice] = usuario_actualizado
            return {"mensaje": "Usuario actualizado", "datos": usuarios[indice]}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.patch("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD'])
async def actualizar_usuario_parcial(usuario_id: int, datos_parciales: dict):
    """PATCH: Modifica solo los campos enviados."""
    for usr in usuarios:
        if usr["id"] == usuario_id:
            usr.update(datos_parciales)
            return {"mensaje": "Usuario actualizado parcialmente", "usuario": usr}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.delete("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD'])
async def eliminar_usuario(usuario_id: int):
    """DELETE: Elimina al usuario de la lista."""
    for i, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuario_eliminado = usuarios.pop(i)
            return {"mensaje": "Usuario eliminado", "usuario": usuario_eliminado}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")