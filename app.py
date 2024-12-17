from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict
import os
import json
import logging
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from logging.handlers import RotatingFileHandler

# Configuración del sistema de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# Crear un manejador para archivo que rota
file_handler = RotatingFileHandler(
    "api.log",
    maxBytes=10485760,  # 10MB
    backupCount=5,
    encoding="utf-8"
)

# Formato del log
log_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

app = FastAPI()

# Variables para el healthcheck
START_TIME = datetime.now()
REQUESTS_FILE = "requests.txt"

# Middleware para logging
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Tiempo de inicio de la petición
        start_time = datetime.now()
        
        # Obtener el cuerpo de la petición
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
            except:
                body = await request.body()

        # Log de la petición entrante
        logger.info(
            f"Incoming request - Method: {request.method} "
            f"Path: {request.url.path} "
            f"Client: {request.client.host} "
            f"Headers: {dict(request.headers)} "
            f"Body: {body}"
        )

        # Procesar la petición
        response = await call_next(request)
        
        # Calcular tiempo de procesamiento
        process_time = (datetime.now() - start_time).total_seconds()

        # Log de la respuesta
        logger.info(
            f"Response - Status: {response.status_code} "
            f"Process Time: {process_time:.3f}s"
        )

        return response

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agregar el middleware de logging
app.add_middleware(LoggingMiddleware)

def save_request(request_data: Dict):
    """Guarda la petición en el archivo de texto"""
    record = {
        "timestamp": datetime.now().isoformat(),
        "data": request_data
    }
    
    with open(REQUESTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    
    logger.info(f"Request saved to file: {record}")

def read_requests():
    """Lee todas las peticiones del archivo"""
    if not os.path.exists(REQUESTS_FILE):
        logger.warning(f"Requests file not found: {REQUESTS_FILE}")
        return []
    
    requests = []
    try:
        with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    requests.append(json.loads(line))
        logger.info(f"Successfully read {len(requests)} requests from file")
    except Exception as e:
        logger.error(f"Error reading requests file: {str(e)}")
        return []
    
    return requests

@app.post("/")
async def root(body: Dict):
    logger.info(f"Processing POST request with body: {body}")
    save_request(body)
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
    response = {
        "status": "ok",
        "uptime": str(uptime),
        "timestamp": datetime.now().isoformat(),
        "service": "FastAPI Server",
        "version": "1.0.0"
    }
    logger.info(f"Health check performed: {response}")
    return response

@app.get("/requests")
async def get_requests():
    """Endpoint para obtener todas las peticiones guardadas"""
    logger.info("Retrieving all saved requests")
    return read_requests()

if __name__ == "__main__":
    import uvicorn
    # Obtener el puerto de la variable de entorno WEBSITES_PORT o usar 80 por defecto
    port = int(os.environ.get("WEBSITES_PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
