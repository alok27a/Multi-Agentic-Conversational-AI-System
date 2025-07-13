# Multi-Agentic Conversational AI System

This project is a full-stack application featuring a **Python (FastAPI)** backend and a **React (Chakra UI)** frontend. It provides a sophisticated conversational AI system that allows users to "talk" to structured data (CSVs) using natural language.

The backend leverages a **Text-to-SQL architecture**, an advanced form of **Retrieval-Augmented Generation (RAG)**, to translate user questions into precise database queries, ensuring high accuracy. A **MongoDB-based CRM** captures all user and conversation data, including AI-generated tags for categorization.

---

## Key Features

- **Advanced RAG with Text-to-SQL**  
  The system uses a highly precise implementation of Retrieval-Augmented Generation. It converts natural language questions into SQL queries, which are then executed against a **SQLite database** populated from a user-uploaded CSV.

- **Conversational Memory**  
  The AI maintains full context of the current conversation, allowing for natural follow-up questions.

- **Full-Fledged CRM**  
  A **MongoDB-backed CRM** stores user profiles and complete, queryable conversation histories.

- **Automated Conversation Tagging**  
  A background process uses an LLM to analyze conversations and automatically apply relevant tags (e.g., _"Property Inquiry," "Price Comparison"_) to the CRM records.

- **Modern Frontend**  
  A responsive and user-friendly frontend built with **React and Chakra UI**, providing a seamless user experience for authentication, file uploads, and chatting.

- **Secure Authentication**  
  The backend includes secure user authentication with password hashing.

---

## Architectural Evolution: From Vector RAG to Text-to-SQL

The initial project requirements suggested a standard **Retrieval-Augmented Generation (RAG)** approach, typically involving a vector database like **FAISS**. While powerful for unstructured text, this method has limitations when applied to highly structured data like a CSV.

### The Challenge with Standard RAG and FAISS

- **Lack of Precision**  
  A query for _"15 West 38th Street"_ might be semantically close to _"36 West 36th Street"_ due to similar terms. However, cosine similarity doesn’t recognize them as fundamentally different addresses. It struggles with **exact-match filtering**.

- **Context Dilution**  
  Embedding an entire CSV row into a single vector dilutes the importance of individual data points. A vector for a property with high rent might be "far away" from one with low rent, even if they're at the same location.

---

## The Solution: Text-to-SQL

To solve these issues, the project evolved to a more precise **Text-to-SQL** model — a more advanced form of RAG:

- The **"retrieval"** step becomes SQL query generation.
- The **"augmentation"** step becomes executing that query to fetch exact, filtered data from the database.

This approach combines the **precision of a database query** with the **flexibility of a natural language interface**, making it ideal for interacting with structured data like CSVs.


## System Architecture


## Sample Converstions
If you are running the backend on your local machine please feel free to go to FastAPI Docs at this URL `http://127.0.0.1:8000/docs#/` and use the swagger UI. Or for convineance I have created a frontend as well, which can be used very easily. 


## Setup & Usage

To run this project, you will need **Node.js** and **npm** installed.

### Clone the Repository

```bash
git clone [your-repo-link]
cd [your-repo-name]
```
## Backend Setup

1. Navigate to the backend directory:
```bash
   cd backend
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a .env file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=YOUR_ACTUAL_OPENAI_API_KEY
MONGO_URI = 
DB_NAME="multi_agent_db"
```

4. Start the backend server:

```
uvicorn app.main:app --reload
```

## Frontend Setup
1. Navigate to the frontend directory:
```bash
   cd backend
```
2. Install dependencies:
```bash
npm install
```
3. Start the server:
```
npm run start
```