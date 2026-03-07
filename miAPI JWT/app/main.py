from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field

#CONFIGURACIONES OAUTH2 Y JWT
SECRET_KEY = "mi_clave_secreta_super_segura" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

usuarios = [
    {"id": 1, "nombre": "Santiago", "edad": 21},
    {"id": 2, "nombre": "Sergio", "edad": 22},
    {"id": 3, "nombre": "Rodrigo", "edad": 20},
]

class crear_usuario(BaseModel):
    id: int = Field(..., gt=0, description="Identificador unico")
    nombre: str = Field(..., min_length=3, max_length=50, example="Jesus")
    edad: int = Field(..., ge=1, le=100, description="Edad valida entre 1 y 100")

#GENERACIÓN DE TOKENS
def crear_token_acceso(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire}) 
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token", tags=['Seguridad'])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or form_data.password != "secreto":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tiempo_expiracion = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = crear_token_acceso(
        data={"sub": form_data.username}, expires_delta=tiempo_expiracion
    )
    return {"access_token": token, "token_type": "bearer"}


#IMPLEMENTAR VALIDACIÓN DE TOKENS
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

#RUTAS 
@app.get("/v1/usuarios/", tags=['HTTP CRUD'])
async def leer_usuarios():
    return {"total": len(usuarios), "usuarios": usuarios}

@app.post("/v1/usuarios/", tags=['HTTP CRUD'], status_code=status.HTTP_201_CREATED)
async def crear_usuario_endpoint(usuario: crear_usuario):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(status_code=400, detail="El id ya existe")
    usuarios.append(usuario.dict())
    return {"mensaje": "Usuario Creado", "datos": usuario}

@app.patch("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD'])
async def actualizar_usuario_parcial(usuario_id: int, datos_parciales: dict):
    for usr in usuarios:
        if usr["id"] == usuario_id:
            usr.update(datos_parciales)
            return {"mensaje": "Usuario actualizado parcialmente", "usuario": usr}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

#RUTAS PROTEGIDAS 
@app.put("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD Protegido'])
async def actualizar_usuario_completo(usuario_id: int, usuario_actualizado: dict, usuario_actual: str = Depends(verificar_token)):
    for indice, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuarios[indice] = usuario_actualizado
            return {"mensaje": f"Usuario actualizado por admin {usuario_actual}", "datos": usuarios[indice]}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@app.delete("/v1/usuarios/{usuario_id}", tags=['HTTP CRUD Protegido'])
async def eliminar_usuario(usuario_id: int, usuario_actual: str = Depends(verificar_token)):
    for i, usr in enumerate(usuarios):
        if usr["id"] == usuario_id:
            usuario_eliminado = usuarios.pop(i)
            return {"mensaje": f"Usuario eliminado por admin {usuario_actual}", "usuario": usuario_eliminado}
    raise HTTPException(status_code=404, detail="Usuario no encontrado")