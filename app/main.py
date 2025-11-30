from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.routes.faturamento import router as faturamento_router
from app.routes.produtos import router as produtos_router
from app.routes.servicos import router as servicos_router
from app.routes.fidelidade import router as fidelidade_router
from app.utils.auth import validate_token

app = FastAPI(title="Duzz Commercial BFF API", version="1.0.0")

# Global middleware for authentication
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Skip authentication for root endpoint and docs
    if request.url.path in ["/", "/docs", "/openapi.json", "/redoc", "/health"]:
        return await call_next(request)
    
    # Validate headers for all other endpoints
    sessiontoken = request.headers.get("sessiontoken")
    company = request.headers.get("company")
    
    if not sessiontoken or not company:
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing sessionToken or company header"}
        )
    
    # Validate token using the existing auth logic
    try:
        # Validate the token - this will raise HTTPException if invalid
        validate_token(sessiontoken, company)
        
        # Store headers in request state for service functions to use
        request.state.auth_headers = (("company", company), ("sessionToken", sessiontoken))
        
        # If validation passes, continue with the request
        response = await call_next(request)
        return response
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )
    except Exception:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or expired sessionToken"}
        )

# Include all routes
app.include_router(faturamento_router, prefix="/api")
app.include_router(produtos_router, prefix="/api")
app.include_router(servicos_router, prefix="/api")
app.include_router(fidelidade_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Backend for Frontend (BFF) is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Duzz Commercial BFF"}
