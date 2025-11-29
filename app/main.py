from fastapi import FastAPI
from app.routes.faturamento import router as faturamento_router

app = FastAPI()

# Include routes here in the future
app.include_router(faturamento_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Backend for Frontend (BFF) is running!"}