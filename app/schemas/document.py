import uuid
from pydantic import BaseModel


class DocumentRequest(BaseModel):
    file_name: str
    file_path: str

class DocumentChunkRequest(BaseModel):
    document_id: uuid.UUID
    content: str
    chunk_index: int
    page_number: int
    embedding: list[float]