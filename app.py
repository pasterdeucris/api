from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
import os

app = FastAPI()

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

if __name__ == "__main__":
    import uvicorn
    # Obtener el puerto de la variable de entorno WEBSITES_PORT o usar 80 por defecto
    port = int(os.environ.get("WEBSITES_PORT", 80))
    uvicorn.run(app, host="0.0.0.0", port=port)
