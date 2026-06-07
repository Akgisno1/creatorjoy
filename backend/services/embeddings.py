from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from services.supabase_client import get_supabase

_model = SentenceTransformer("BAAI/bge-small-en-v1.5")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_DIM = 384


def chunk_text(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


def embed_text(text: str) -> list[float]:
    return _model.encode(text, normalize_embeddings=True).tolist()


def embed_query(text: str) -> list[float]:
    return _model.encode(
        f"Represent this sentence for searching: {text}",
        normalize_embeddings=True,
    ).tolist()


async def chunk_and_embed(session_id: str, video_id: str, transcript: str):
    sb = get_supabase()
    chunks = chunk_text(transcript)

    rows = []
    for i, chunk in enumerate(chunks):
        embedding = embed_text(chunk)
        rows.append({
            "session_id": session_id,
            "video_id": video_id,
            "chunk_index": i,
            "content": chunk,
            "embedding": embedding,
        })

    sb.table("transcript_chunks").insert(rows).execute()