from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def chats_placeholder():
    return {"message": "chats router ready"}