from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def ingest_placeholder():
    return {"message": "ingest router ready"}