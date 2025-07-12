from openai import AsyncOpenAI
from app.core.config import settings
from typing import List, Dict

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def get_llm_response(system_prompt: str, conversation_history: List[Dict[str, str]]) -> str:
    """
    Gets a response from the OpenAI LLM.
    
    Args:
        system_prompt: The detailed instructions and context for the AI.
        conversation_history: The list of previous messages in the conversation.
    
    Returns:
        The text response from the language model.
    """
    messages = [
        {"role": "system", "content": system_prompt}
    ] + conversation_history
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3, # Lowered for higher factual accuracy
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Sorry, I encountered an error and can't respond right now."
