from openai import AsyncOpenAI
from app.core.config import settings
from typing import List, Dict
import json

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def generate_sql_from_prompt(prompt: str) -> str:
    """Generates a SQL query from a natural language prompt."""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates SQLite queries based on user questions and a database schema. Only return the SQL query, with no other text or explanation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
        )
        sql_query = response.choices[0].message.content.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:-3].strip()
        return sql_query
    except Exception as e:
        print(f"Error generating SQL query: {e}")
        return "SELECT 'Error generating query';"

async def synthesize_response_from_sql(user_question: str, sql_query: str, sql_results: str) -> str:
    """Generates a natural language response from the SQL query and its results."""
    prompt = (
        f"You are a helpful assistant. The user asked the following question: '{user_question}'.\n"
        f"To answer this, the following SQL query was run: '{sql_query}'.\n"
        f"The result of the query was: \n{sql_results}\n\n"
        "Please synthesize a clear, natural language response to the user's original question based on these results."
    )
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error synthesizing response: {e}")
        return "I found some data, but I'm having trouble interpreting it."

async def generate_tags_for_conversation(conversation_history: str) -> List[str]:
    """Analyzes a conversation and generates a list of relevant tags."""
    prompt = (
        "You are a helpful assistant that categorizes conversations. Based on the following conversation history, "
        "generate a JSON list of 1 to 3 relevant tags. Example tags include: 'Property Inquiry', 'Price Comparison', "
        "'Specific Unit Question', 'Resolved', 'Unresolved', 'General Question'.\n\n"
        f"Conversation History:\n{conversation_history}\n\n"
        "JSON Tag List:"
    )
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        # The response is expected to be a JSON object like {"tags": ["tag1", "tag2"]}
        tags_data = json.loads(response.choices[0].message.content)
        return tags_data.get("tags", [])
    except Exception as e:
        print(f"Error generating tags: {e}")
        return []