import asyncio
from math import lgamma
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
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

async def get_document(session: AsyncSession) -> list[Document]:
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

async def hybrid_search(session: AsyncSession, query_text: str, embedding: list[float], limit: int = 5) -> list[DocumentChunk]:
    vector_result, text_result = await asyncio.gather(
        session.execute(
            select(DocumentChunk)
            .order_by(DocumentChunk.embedding.cosine_distance(embedding))
            .limit(limit=limit*2)
        ),
        session.execute(
            select(DocumentChunk)
            .order_by(func.similarity(DocumentChunk.content, query_text).desc())
            .limit(limit=limit*2)
        )
    )

    vector_chunks = vector_result.scalars().all()
    text_chunks = text_result.scalars().all()

    rrf_scores = {}

    for rank, chunk in enumerate(vector_chunks, start=1):
        rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0) + 1 / (60+rank)

    for rank, chunk in enumerate(text_chunks, start=1):
        rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0) + 1 / (60+rank)

    all_chunk = {chunk.id: chunk for chunk in vector_chunks + text_chunks}

    sorted_ids = sorted(rrf_scores, key=lambda id: rrf_scores[id], reverse=True)

    return [all_chunk[id] for id in sorted_ids[:limit]]
