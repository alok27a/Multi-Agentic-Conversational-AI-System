from openai import AsyncOpenAI
from app.core.config import settings
from typing import List
import json

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_tags_for_conversation(conversation_history: str) -> List[str]:
    prompt = (
        "You are a helpful assistant that categorizes conversations. Based on the following conversation history, "
        "generate a JSON list of 1 to 3 relevant tags. Example tags include: 'Property Inquiry', 'Price Comparison', "
        "'Specific Unit Question', 'Resolved', 'Unresolved', 'General Question'.\n\n"
        f"Conversation History:\n{conversation_history}\n\n"
        'Respond with a JSON object like {"tags": ["tag1", "tag2"]}.'
    )
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        tags_data = json.loads(response.choices[0].message.content)
        return tags_data.get("tags", [])
    except Exception as e:
        print(f"Error generating tags: {e}")
        return []
