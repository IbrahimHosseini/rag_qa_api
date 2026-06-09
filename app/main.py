from fastapi import FastAPI
from .routers import documents

app = FastAPI(
    title="RAG qa API",
    description=" API for QA in RAG system",
    version="0.1.0"
)

app.include_router(documents.router)