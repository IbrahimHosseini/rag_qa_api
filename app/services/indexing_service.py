import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from .embedding_service import get_embeddings
from .pdf_parser import pdf_parser
from .text_splitter import split_text
from db.repository import document_repository
from app.schemas.document import DocumentChunkRequest

async def index_document(path: str, document_id: uuid.UUID, session: AsyncSession) -> None :
    
    pdf_data = pdf_parser(path=path)

    for data in pdf_data:
        chunks = split_text(data[1])
        embeddings = await get_embeddings(chunks)

        document_chunks: list[DocumentChunkRequest] = []
        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            new_doc_chunk = DocumentChunkRequest(
                document_id=document_id,
                content=chunk,
                chunk_index=index,
                page_number=data[0],
                embedding=embedding
            )
            document_chunks.append(new_doc_chunk)
            
        await document_repository.create_document_chunk(session=session, document_chunks=document_chunks)
