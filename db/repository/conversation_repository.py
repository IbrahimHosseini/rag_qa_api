

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.document import ConversationRequest
from db.models import ConversationHistory

async def add_message(session: AsyncSession, conversation: ConversationRequest) -> ConversationHistory | None:
    new_conversation = ConversationHistory(
        session_id=conversation.session_id,
        role=conversation.role,
        content=conversation.content
    )

    session.add(new_conversation)
    await session.flush()
    await session.refresh(new_conversation)

    return new_conversation


async def get_history(session: AsyncSession, session_id: uuid.UUID) -> list[ConversationHistory]:
    result = await session.execute(
        select(ConversationHistory)
        .where(ConversationHistory.session_id == session_id)
        .order_by(ConversationHistory.created_at.asc())
    )

    return result.scalars().all()