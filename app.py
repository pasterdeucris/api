from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict
import os
from datetime import datetime

app = FastAPI()

# Variables para el healthcheck
START_TIME = datetime.now()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/")
async def root(body: Any):
    return body

@app.get("/health")
async def health_check() -> Dict:
    """
    Endpoint de healthcheck que retorna:
    - status: estado del servicio
    - uptime: tiempo que lleva ejecutándose el servicio
    - timestamp: hora actual
    """
    uptime = datetime.now() - START_TIME
    return {
        "status": "ok",
        "uptime": str(uptime),
        "timestamp": datetime.now().isoformat(),
        "service": "FastAPI Server",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    # Obtener el puerto de la variable de entorno WEBSITES_PORT o usar 80 por defecto
    port = int(os.environ.get("WEBSITES_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
