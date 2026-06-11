import uuid
from pydantic import BaseModel, ConfigDict
from db.models import Role, Status
from datetime import datetime
from enum import Enum

class DocumentRequest(BaseModel):
    file_name: str
    file_path: str

class DocumentChunkRequest(BaseModel):
    document_id: uuid.UUID
    content: str
    chunk_index: int
    page_number: int
    embedding: list[float]

class DocumentResponse(BaseModel):
    id: uuid.UUID
    file_name: str
    file_path: str
    status: Status

    model_config = ConfigDict(from_attributes=True)

class SearchResponse(BaseModel):
    id: uuid.UUID
    content: str

    model_config = ConfigDict(from_attributes=True)

class SearchRequest(BaseModel):
    text: str

class ConversationRequest(BaseModel):
    session_id: uuid.UUID
    role: Role
    content: str

class ChatResponse(BaseModel):
    session_id: uuid.UUID
    query: str
    rephrased_query: str
    results: list[SearchResponse]

class ChatRequest(BaseModel):
    session_id: uuid.UUID
    query: str