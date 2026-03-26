#Importaciones
from fastapi import FastAPI
from app.router import usuario
from app.router import misc
from app.data.db import engine
from app.data import usuario as usuarioDB

usuarioDB.Base.metadata.create_all(bind=engine)

#Instancia del Servidor
app = FastAPI(
    title="Mi primer Api",
    description= "Brian Barron Arteaga",
    version="1.0"
)

app.include_router(usuario.router)
app.include_router(misc.misc)
