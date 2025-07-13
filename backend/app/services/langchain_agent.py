from langchain_openai import ChatOpenAI
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from app.core.config import settings
from app.services.text_to_sql_service import text_to_sql_service
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.agents.agent_types import AgentType

# Initialize the database connection for LangChain
db = SQLDatabase.from_uri(text_to_sql_service.get_db_uri())

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=settings.OPENAI_API_KEY)

# Create the SQL agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Setup memory for conversational context
memory = ConversationBufferMemory(
    memory_key="chat_history", 
    input_key='input', 
    output_key="output", 
    return_messages=True
)

# Add a placeholder for chat history in the agent's prompt
agent_kwargs = {
    "extra_prompt_messages": [MessagesPlaceholder(variable_name="chat_history")],
}

# Create the agent executor
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    agent_kwargs=agent_kwargs,
    memory=memory,
    handle_parsing_errors=True, # Gracefully handle errors if the LLM outputs a malformed query
)

async def invoke_agent(user_question: str, chat_history: list):
    """
    Invokes the LangChain SQL agent with the user's question and conversation history.
    """
    try:
        # The agent will automatically use the chat history from memory
        response = await agent_executor.ainvoke({"input": user_question, "chat_history": chat_history})
        return response.get("output", "I'm sorry, I couldn't process that request.")
    except Exception as e:
        print(f"Error invoking LangChain agent: {e}")
        return "An error occurred while processing your request with the agent."

