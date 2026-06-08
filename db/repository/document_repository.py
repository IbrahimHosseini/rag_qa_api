import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from db.models import Document, DocumentChunk, Status
from app.schemas.document import DocumentRequest, DocumentChunkRequest

async def create_document(session: AsyncSession, document: DocumentRequest) -> Document | None:
    new_document = Document(
        file_name = document.file_name,
        file_path = document.file_path
    )

    session.add(new_document)
    await session.flush()
    await session.refresh(new_document)

    return new_document

async def get_document(session: AsyncSession) -> Document | None:
    result = await session.execute(select(Document))

    return result.scalars().all()

async def update_document_status(session: AsyncSession, document_id: uuid.UUID, status: Status) -> Document | None:
    result = await session.execute(
        select(Document).where(Document.id == document_id)
    )

    document = result.scalar_one_or_none()

    if document is None:
        return None

    document.status = status

    await session.flush()
    await session.refresh(document)

    return document

async def create_document_chunk(session: AsyncSession, document_chunks: list[DocumentChunkRequest]) -> list[DocumentChunk] | None:
    new_document_chunks = []

    for dc in document_chunks:
        new_chunk = DocumentChunk(
            content=dc.content,
            chunk_index=dc.chunk_index,
            page_number=dc.page_number,
            embedding=dc.embedding,
            document_id=dc.document_id
        )
        new_document_chunks.append(new_chunk)

    session.add_all(new_document_chunks)
    await session.flush()
    for chunk in new_document_chunks:
        await session.refresh(chunk)
    
    return new_document_chunks

async def search_content(session: AsyncSession, embedding: list[float], limit: int = 5) -> list[DocumentChunk] | None:
    result = await session.execute(
        select(DocumentChunk)
        .order_by(DocumentChunk.embedding.cosine_distance(embedding))
        .limit(limit=limit)
    )

    return result.scalars().all()