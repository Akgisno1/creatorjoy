from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import ingest, chat, chats
import os

load_dotenv()

app=FastAPI(title="CreatorJoy API",version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL","http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status":"ok"}

app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(chat.router,   prefix="/chat",   tags=["chat"])
app.include_router(chats.router,  prefix="/chats",  tags=["chats"])