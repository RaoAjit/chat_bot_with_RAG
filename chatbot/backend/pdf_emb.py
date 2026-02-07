from memory import add_to_memory,get_memory_context
import pdfplumber, io
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        openai_api_key=OPENAI_API_KEY
    )

def pdf_embedding(pdf_bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
            if page_text:
                text += page_text + "\n"
   
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(text)
    embeddings = OpenAIEmbeddings()

    vector_db = FAISS.from_texts(chunks, embeddings)
    print("Total vectors stored:", vector_db.index.ntotal)
    return vector_db

#pdf_vector_store = pdf_embedding(pdf_bytes)
def answer_from_pdf(user_query,pdf_vector_store):
    docs = pdf_vector_store.similarity_search(user_query, k=3)
    context = " ".join(doc.page_content for doc in docs)
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