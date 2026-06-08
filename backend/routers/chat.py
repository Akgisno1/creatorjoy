import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest
from services.supabase_client import get_supabase
from services.rag import (
    build_context,
    build_messages,
    SYSTEM_PROMPT,
    llm,
    get_chat_history,
)

router = APIRouter()


@router.post("/")
async def chat(req: ChatRequest):
    sb = get_supabase()

    try:
        sb.table("messages").insert({
            "chat_id": req.chat_id,
            "role": "user",
            "content": req.message,
        }).execute()

        context, metadata_str, citations = build_context(req.session_id, req.message)

        history = get_chat_history(req.chat_id)
        history = history[:-1]

        system = SYSTEM_PROMPT.format(context=context, metadata=metadata_str)
        messages = build_messages(system, history, req.message)

        async def generate():
            full_response = ""
            async for chunk in llm.astream(messages):
                token = chunk.content
                if token:
                    full_response += token
                    yield f"data: {json.dumps({'token': token})}\n\n"

            sb.table("messages").insert({
                "chat_id": req.chat_id,
                "role": "assistant",
                "content": full_response,
                "citations": citations,
            }).execute()

            yield f"data: {json.dumps({'done': True, 'citations': citations})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    except Exception as e:
        async def error_stream():
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")