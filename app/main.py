from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routes.faturamento import router as faturamento_router
from routes.produtos import router as produtos_router
from routes.servicos import router as servicos_router
from routes.fidelidade import router as fidelidade_router
from routes.metricas import router as metricas_router
from utils.auth import validate_token

app = FastAPI(title="Duzz Commercial BFF API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(faturamento_router, prefix="/api")
app.include_router(produtos_router, prefix="/api")
app.include_router(servicos_router, prefix="/api")
app.include_router(fidelidade_router, prefix="/api")
app.include_router(metricas_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Backend for Frontend (BFF) is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Duzz Commercial BFF"}
