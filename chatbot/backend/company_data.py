from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os
from memory import add_to_memory,get_memory_context
from utils import dbsearch_answer
import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DIR = os.path.join(BASE_DIR, "vectorstore_routes")
# -----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
'''embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=OPENAI_API_KEY
    )

db = Chroma(
    persist_directory=VECTOR_DIR,
    embedding_function=embeddings
)'''
llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        openai_api_key=OPENAI_API_KEY
    )
# -----------------------------

def answer(user_query):
    results = dbsearch_answer(user_query)
    context = "\n".join([doc.page_content for doc in results])
    history = get_memory_context()

    if not context.strip() and not history.strip():
        return "I don't have that information."

    prompt = ChatPromptTemplate.from_template("""
You are a helpful enterprise route assistant.

Conversation History:
{history}

Knowledge Context:
{context}

Rules:
- Prefer Knowledge Context
- Use Conversation History only if needed
- Do NOT guess

User Question:
{question}

Answer clearly and concisely:
""")

    response = llm.invoke(
        prompt.format(
            history=history,
            context=context,
            question=user_query
        )
    )

    add_to_memory(user_query, response.content)
    return response.content




#print(answer(user_query="what is fastapi"))