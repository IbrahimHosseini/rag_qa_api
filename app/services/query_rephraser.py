
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from db.models import ConversationHistory
import openai

client = openai.AsyncOpenAI(api_key= settings.OPENAI_API_KEY)

async def rephraser(query: str, history:list[ConversationHistory]) -> str:
    if not history:
        return query
    
    history_text = "\n".join([
        f"{msg.role}: {msg.content}"
        for msg in history
    ])

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Given the conversation history and the follow-up question, rephrase the follow-up question to be a standalone question. Return only the rephrased question, nothing else."
            },
            {
                "role": "user",
                "content": f"Conversation history:\n{history_text}\n\nFollow-up question: {query}"
            }
        ],
        temperature=0 
    )

    return response.choices[0].message.content
