from sentence_transformers import CrossEncoder
from db.models import DocumentChunk
import asyncio

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

async def rerank(query: str, chunks: list[DocumentChunk], top_k: int = 3) -> list[DocumentChunk]:
    
    pairs = [(query, chunk.content) for chunk in chunks]

    scores = await asyncio.get_event_loop().run_in_executor(
        None,
        model.predict,
        pairs
    )

    chunk_score_pairs = sorted(
        zip(chunks, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [chunk for chunk, score in chunk_score_pairs[:top_k]]