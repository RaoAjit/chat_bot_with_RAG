from memory import add_to_memory,get_memory_context
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        openai_api_key=OPENAI_API_KEY
    )

def url_data_embeding(url):
    loader = WebBaseLoader([url])
    documents = loader.load()

    # Split text
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    chunks = splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    vector_db = FAISS.from_documents(chunks, embeddings)
    print("Total vectors stored:", vector_db.index.ntotal)
    return vector_db

def data_from_url(user_query,pdf_vector_store):
    docs = pdf_vector_store.similarity_search(user_query, k=3)
    context = " ".join(doc.page_content for doc in docs)
    print(user_query)
    print(context)
    history = get_memory_context()
    prompt = ChatPromptTemplate.from_template("""
You are a helpful AI assistant.

Answer the user's question ONLY using the context provided below.
Do NOT use outside knowledge.
If the answer is not present in the context, say:
"I could not find this information in the uploaded document."

Keep the answer:
- Clear
- Concise
- Fact-based
- Professional


Context:
{context}

Question:
{question}

Answer:""")
    response = llm.invoke(
        prompt.format(
            history=history,
            context=context,
            question=user_query
        )
    )
 
    add_to_memory(user_query, response.content)
    return response.content