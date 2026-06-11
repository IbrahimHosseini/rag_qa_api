from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from app.services import reranker
from app.services.indexing_service import index_document
from app.services.embedding_service import get_embedding
from app.services.query_rephraser import rephraser
from app.services.reranker import rerank
from db.models import Role
from db.session import get_db
from app.schemas.document import ChatResponse, ConversationRequest, DocumentRequest, DocumentResponse, SearchRequest, SearchResponse, ChatRequest
from db.repository import document_repository, conversation_repository
import shutil, uuid
from pathlib import Path

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {".pdf"}

@router.post("/",response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), session=Depends(get_db)):
    
    file_ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR/unique_name

    if file_ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document_request = DocumentRequest(file_name=unique_name, file_path=str(file_path))

    try:
        new_document = await document_repository.create_document(session=session, document=document_request)
        await index_document(path=str(file_path), document_id=new_document.id, session=session)
        await session.commit()
        return new_document
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/", response_model=list[DocumentResponse])
async def get_documents(session=Depends(get_db)):
    response = await document_repository.get_document(session=session)
    return response

@router.post("/search", response_model=list[SearchResponse])
async def search(content: SearchRequest, session=Depends(get_db)):
    embedding = await get_embedding(content.text)
    results = await document_repository.hybrid_search(session=session, query_text= content.text, embedding=embedding)
    reranked = await rerank(query=content.text, chunks= results)
    return reranked

@router.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, session=Depends(get_db)):

    history = await conversation_repository.get_history(
        session=session, 
        session_id=chat_request.session_id
    )

    rephrased = await rephraser(query=chat_request.query, history=history)

    embedding = await get_embedding(rephrased)
    results = await document_repository.hybrid_search(
        session=session, 
        query_text= rephrased, 
        embedding=embedding
    )
    reranked = await rerank(query=chat_request.query, chunks= results)

    conversation_request = ConversationRequest(
        session_id=chat_request.session_id,
        role=Role.user,
        content=chat_request.query
    )

    await conversation_repository.add_message(
        session=session,
        conversation=conversation_request
    )

    await session.commit()

    return ChatResponse(
        session_id=chat_request.session_id,
        query=chat_request.query,
        rephrased_query=rephrased,
        results=reranked
    )

