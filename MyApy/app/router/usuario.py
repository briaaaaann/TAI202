from fastapi import FastAPI, status, HTTPException, Depends, APIRouter
from app.models.usuario import crear_usuario
from app.data.database import usuarios
from app.security.auth import verificar_peticion

from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data.usuario import usuario as dbUsuario

#********************
#ROUTER
#********************
router=APIRouter(
    prefix="/v1/usuarios",
    tags=["HTTP CRUD"]
)

#********************
#Usuarios CRUD
#********************
@router.get("/")
def leer_usuarios(db:Session=Depends(get_db)):
    queryUsuarios=db.query(dbUsuario).all()
    return {
        "status":"200",
        "total": len(queryUsuarios), 
        "usuarios": queryUsuarios
    }

@router.get("/{usuario_id}")
def leer_usuario(usuario_id: int, db: Session = Depends(get_db)):
    queryUsuario = db.query(dbUsuario).filter(dbUsuario.id == usuario_id).first()
    
    if not queryUsuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    return {
        "status": "200",
        "usuario": queryUsuario
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_usuarios(usuarioP: crear_usuario,db:Session=Depends(get_db)):
    nuevoU= dbUsuario(nombre= usuarioP.nombre,edad= usuarioP.edad)
    db.add(nuevoU)
    db.commit()
    db.refresh(nuevoU)

    return {
        "mensaje": "Usuario Agregado", 
        "Usuario": usuarioP
    }

@router.put("/{usuario_id}")
def actualizar_usuario_completo(usuario_id: int, usuario_actualizado: crear_usuario, db: Session = Depends(get_db)):
    usuario_db = db.query(dbUsuario).filter(dbUsuario.id == usuario_id).first()
    
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario_db.nombre = usuario_actualizado.nombre
    usuario_db.edad = usuario_actualizado.edad
    
    db.commit()
    db.refresh(usuario_db)
    return {"mensaje": "Usuario actualizado", "datos": usuario_db}


@router.patch("/{usuario_id}")
def actualizar_usuario_parcial(usuario_id: int, datos_parciales: dict, db: Session = Depends(get_db)):
    usuario_db = db.query(dbUsuario).filter(dbUsuario.id == usuario_id).first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    for key, value in datos_parciales.items():
        if hasattr(usuario_db, key):
            setattr(usuario_db, key, value)
    db.commit()
    db.refresh(usuario_db)
    return {"mensaje": "Usuario actualizado parcialmente", "usuario": usuario_db}


@router.delete("/{usuario_id}")
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db), usuarioAuth: str = Depends(verificar_peticion)):
    usuario_db = db.query(dbUsuario).filter(dbUsuario.id == usuario_id).first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario_db)
    db.commit()
    return {"mensaje": f"Usuario con ID {usuario_id} eliminado por {usuarioAuth}"}


