from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from uuid import UUID

class IngestRequest(BaseModel):
    video_a_url:str
    video_b_url:str
    user_id:Optional[str]=None

class VideoMetadataOut(BaseModel):
    video_id:str
    platform:str
    title:Optional[str]
    creator:Optional[str]
    follower_count:Optional[int]
    views:Optional[int]
    likes:Optional[int]
    comments:Optional[int]
    engagement_rate:Optional[float]
    hashtags:Optional[List[str]]
    duration_seconds:Optional[int]

class IngestResponse(BaseModel):
    session_id:str
    chat_id:str
    video_a:VideoMetadataOut
    video_b:VideoMetadataOut

class ChatRequest(BaseModel):
    session_id:str
    chat_id:str
    message:str
    user_id:Optional[str]=None
    
class Citation(BaseModel):
    video_id: str
    chunk_index: int
    content_snippet: str


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    citations: Optional[List[Citation]] = None
    