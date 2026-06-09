import uuid
from pydantic import BaseModel, ConfigDict
from db.models import Status


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