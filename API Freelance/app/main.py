from fastapi import FastAPI, status, HTTPException, Query, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Literal, Optional, List
from datetime import date, datetime, timedelta, timezone
app = FastAPI(title="API Gestión de Proyectos")

# Base de datos en memoria
proyectos = []

# MODELOS PYDANTIC 

class Proyecto(BaseModel):
    id: int = Field(..., gt=0, description="ID único del proyecto")
    nombre: str = Field(..., min_length=5, max_length=80)
    presupuesto: float = Field(..., ge=100.0)
    email_cliente: EmailStr = Field(..., description="Correo válido del cliente")
    estado: Literal["Cotizando", "En desarrollo", "En revision", "Finalizado"] = "Cotizando"
    fecha_entrega: date = Field(..., description="Fecha en formato YYYY-MM-DD")

#-----
#{
#    "id": 1,
#    "nombre": "Sitio Web Corporativo",
#    "presupuesto": 1500.50,
#    "email_cliente": "contacto@empresa.com",
#    "estado": "Cotizando",
#    "fecha_entrega": "2026-12-15"
#}
#-------
    # Validador personalizado para asegurar que la fecha no sea en el pasado
    @field_validator('fecha_entrega')
    @classmethod
    def validar_fecha_futura(cls, v):
        if v < date.today():
            raise ValueError('La fecha del proyecto no puede ser en el pasado')
        return v

class ProyectoUpdate(BaseModel):
    """Modelo para PATCH: Todos los campos son opcionales"""

    titulo: Optional[str] = Field(None, min_length=5, max_length=80)
    presupuesto: Optional[float] = Field(None, ge=100.0)
    email_cliente: Optional[EmailStr] = Field(None, description="Correo válido del cliente")
    estado: Optional[Literal["Cotizando", "En desarrollo", "En revision", "Finalizado"]] = None
    fecha_entrega: Optional[date] = None

    @field_validator('fecha_entrega')
    @classmethod
    def validar_fecha_futura(cls, v):
        if v is not None and v < date.today():
            raise ValueError('La fecha del proyecto no puede ser en el pasado')
        return v

#Configuracion JWT

SECRET_KEY = "super_secreto_proyectos"
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

# ENDPOINTS 

# 1. GET: Leer todos los proyectos (con filtro opcional por estado)
@app.get("/v1/proyectos/", tags=['Proyectos'])
async def obtener_proyeectos(estado: Optional[str] = Query(None, description="Filtrar por estado")):
    if estado:
        filtrados = [e for e in proyectos if e["estado"].lower() == estado.lower()]
        return {"total": len(filtrados), "proyectos": filtrados}
    return {"total": len(proyectos), "proyectos": proyectos}

# 1.1. GET: Leer todos los proyectos (sin filtros)
@app.get("/v1/proyectos/", tags=['Proyectos'])
async def obtener_proyectos():
    # Simplemente devolvemos la longitud de la lista y la lista completa
    return {"total": len(proyectos), "proyectos": proyectos}

#http://localhost:5000/v1/proyectos/1
# 2. POST: Crear un nuevo proyecto
@app.post("/v1/proyectos/{proyecto_id}", status_code=status.HTTP_201_CREATED, tags=['proyectos'])
async def crear_proyecto(proyecto: Proyecto):
    if any(e["id"] == proyecto.id for e in proyectos):
        raise HTTPException(status_code=400, detail="El ID del proyecto ya existe")
    
    proyectos.append(proyecto.model_dump())
    return {"mensaje": "proyecto creado exitosamente", "proyecto": proyecto}

# 3. PUT: Reemplazo total del recurso
@app.put("/v1/proyectos/{proyecto_id}", tags=['Proyectos'])
async def actualizar_proyecto_completo(proyecto_id: int, proyecto_actualizado: Proyecto):
    """PUT requiere que envíes TODOS los campos del modelo para reemplazar el existente."""
    for indice, proyecto in enumerate(proyectos):
        if proyecto["id"] == proyecto_id:
            # Reemplazamos el diccionario completo, pero mantenemos el ID original por seguridad
            nuevo_proyecto = proyecto_actualizado.model_dump()
            nuevo_proyecto["id"] = proyecto_id 
            proyectos[indice] = nuevo_proyecto
            return {"mensaje": "proyecto reemplazado (PUT)", "proyecto": proyectos[indice]}
            
    raise HTTPException(status_code=404, detail="proyecto no encontrado")

# 4. PATCH: Actualización parcial del recurso
@app.patch("/v1/proyectos/{proyecto_id}", tags=['proyectos'])
async def actualizar_proyecto_parcial(proyecto_id: int, proyecto_update: ProyectoUpdate):
    """PATCH permite enviar solo los campos que quieres modificar."""
    for proyecto in proyectos:
        if proyecto["id"] == proyecto_id:
            # exclude_unset=True extrae SOLO los campos que el usuario envió en el JSON
            datos_a_actualizar = proyecto_update.model_dump(exclude_unset=True)
            
            # Actualizamos el diccionario original con los nuevos datos
            proyecto.update(datos_a_actualizar)
            return {"mensaje": "proyecto actualizado parcialmente (PATCH)", "proyecto": proyecto}
            
    raise HTTPException(status_code=404, detail="proyecto no encontrado")

# 5. DELETE: Eliminar un proyecto
@app.delete("/v1/proyectos/{proyecto_id}", tags=['Proyectos'])
async def eliminar_proyecto(proyecto_id: int):
    for i, proyecto in enumerate(proyectos):
        if proyecto["id"] == proyecto_id:
            proyecto_eliminado = proyectos.pop(i)
            return {"mensaje": "proyecto eliminado correctamente", "proyecto": proyecto_eliminado}
            
    raise HTTPException(status_code=404, detail="proyecto no encontrado")