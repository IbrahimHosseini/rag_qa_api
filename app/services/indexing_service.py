import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Status

from .embedding_service import get_embeddings
from .pdf_parser import pdf_parser
from .text_splitter import split_text
from db.repository import document_repository
from app.schemas.document import DocumentChunkRequest

async def index_document(path: str, document_id: uuid.UUID, session: AsyncSession) -> None :
    
    try:
        await document_repository.update_document_status(session=session, document_id=document_id, status=Status.processing)

        pdf_data = pdf_parser(path=path)

        for data in pdf_data:
            chunks = split_text(data[1])
            embeddings = await get_embeddings(chunks)

            new_document_chunks: list[DocumentChunkRequest] = []
            for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                new_doc_chunk = DocumentChunkRequest(
                    document_id=document_id,
                    content=chunk,
                    chunk_index=index,
                    page_number=data[0],
                    embedding=embedding
                )
                new_document_chunks.append(new_doc_chunk)
            
            await document_repository.create_document_chunk(session=session, document_chunks=new_document_chunks)

    except Exception as e:
            await document_repository.update_document_status(session=session, document_id=document_id, status=Status.failed)
            raise HTTPException(status_code=500, detail="")

    await document_repository.update_document_status(session=session, document_id=document_id, status=Status.completed)
