#```python
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta, timezone

app = FastAPI(
    title="API de Integración Empresarial",
    version="1.0.0",
    description="Servicio REST para integración de catálogo y stock"
)

# Permitir solicitudes cruzadas desde el frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "clave_secreta_super_segura"
ALGORITHM = "HS256"

# Base de datos simulada en memoria
productos_db = [
    {"id": 1, "nombre": "Módulo ERP Finanzas", "precio": 1200.0, "stock": 10},
    {"id": 2, "nombre": "Sensor Telemetría IoT", "precio": 85.5, "stock": 25}
]

# Modelos de validación de datos
class LoginRequest(BaseModel):
    username: str
    password: str

class ProductoInput(BaseModel):
    nombre: str
    precio: float
    stock: int

# --- ENDPOINTS ---

# 1. Autenticación: genera y retorna un JWT
@app.post("/api/v1/auth/login", tags=["Seguridad"])
def login(credenciales: LoginRequest):
    if credenciales.username == "admin" and credenciales.password == "123456":
        payload = {
            "sub": credenciales.username,
            "exp": datetime.now(timezone.utc) + timedelta(hours=2)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Credenciales inválidas")

# 2. Lectura: GET público para el catálogo
@app.get("/api/v1/productos", tags=["Productos"])
def listar_productos():
    return productos_db

# 3. Creación: POST protegido con Bearer Token
@app.post("/api/v1/productos", status_code=201, tags=["Productos"])
def crear_producto(item: ProductoInput, authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    
    token = authorization.split(" ")[1]
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=403, detail="Token inválido o expirado")

    nuevo_id = len(productos_db) + 1
    nuevo_item = {"id": nuevo_id, **item.model_dump()}
    productos_db.append(nuevo_item)
    return nuevo_item
