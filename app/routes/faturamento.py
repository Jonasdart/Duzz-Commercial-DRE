from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/faturamento")
def get_faturamento():
    return {"message": "Faturamento endpoint placeholder"}