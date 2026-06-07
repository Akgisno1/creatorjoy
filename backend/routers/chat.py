from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def chat_placeholder():
    return {"message": "chat router ready"}