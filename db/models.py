from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, String, ForeignKey
from sqlalchemy import Enum as SAEnum
from pgvector.sqlalchemy import Vector

from .base import Base
from enum import Enum
import uuid
from config import settings

class Status(str, Enum):
    pending="pending"
    processing="processing"
    completed="completed"
    failed="failed"

class Document(Base):
    __tablename__="document"
    file_name: Mapped[str] = mapped_column(String(255), default="")
    file_path: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[Status] = mapped_column(SAEnum(Status), default=Status.pending)

    document_chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk", 
        back_populates="document",
        cascade="all, delete-orphan"
    )

class DocumentChunk(Base):
    __tablename__="document_chunk"
    content: Mapped[str] = mapped_column(Text, default="")
    chunk_index: Mapped[int] = mapped_column(index=True)
    page_number: Mapped[int] = mapped_column(default=0)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.EMBEDDING_DIMENSION))

    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("document.id"))

    document: Mapped["Document"] = relationship(
        "Document", back_populates="document_chunks"
    )