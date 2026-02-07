import os
import pandas as pd
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader

# =========================================================
# 1. PATH SETUP (ABSOLUTE PATHS - CRITICAL)
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DIR = os.path.join(BASE_DIR, "vectorstore_routes")

# =========================================================
# 2. OPENAI CONFIG
# =========================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=OPENAI_API_KEY
)

"https://fastapi.tiangolo.com/",
"https://fastapi.tiangolo.com/tutorial/",
"https://fastapi.tiangolo.com/advanced/",
"https://docs.djangoproject.com/en/stable/intro/overview/",
"https://docs.djangoproject.com/en/stable/intro/tutorial01/",
"https://docs.djangoproject.com/en/stable/intro/tutorial02/",
"https://docs.djangoproject.com/en/stable/topics/http/views/",
"https://docs.djangoproject.com/en/stable/topics/db/models/",
"https://docs.djangoproject.com/en/stable/topics/auth/",
"https://docs.djangoproject.com/en/stable/ref/models/querysets/",
URLS = [
    "https://www.postgresql.org/docs/current/intro-whatis.html",
    "https://www.postgresql.org/docs/current/tutorial-sql.html",
    "https://www.postgresql.org/docs/current/ddl.html",
    "https://www.postgresql.org/docs/current/dml.html",
    "https://www.postgresql.org/docs/current/indexes.html",
    "https://www.postgresql.org/docs/current/transactions.html",
    "https://www.postgresql.org/docs/current/performance-tips.html",
]

# =========================================================
# 3. LOAD EXCEL DATA
# =========================================================

'''df = pd.read_excel(EXCEL_FILE)
df = df.fillna("")

documents = []

for idx, row in df.iterrows():
    text = (
        f"Route starts from {row['start_location']} "
        f"and ends at {row['end_location']}. "
        f"Distance is {row['distance_km']} kilometers "
        f"and the price is {row['price']} rupees."
    )

    documents.append(
        Document(
            page_content=text,
            metadata={
                "start_location": str(row["start_location"]).lower(),
                "end_location": str(row["end_location"]).lower(),
                "distance_km": row["distance_km"],
                "price": row["price"],
                "row_id": idx
            }
        )
    )

print(f"📄 Loaded {len(documents)} routes from Excel")

# =========================================================
# 4. SPLIT DOCUMENTS (SAFE EVEN IF NOT NEEDED)
# =========================================================

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=0
)

chunks = text_splitter.split_documents(documents)

print(f"✂️ Created {len(chunks)} document chunks")

# =========================================================
# 5. CREATE & PERSIST CHROMA VECTOR STORE
# =========================================================

# ❗ Delete old vectorstore if it exists (optional but recommended)
if os.path.exists(VECTOR_DIR):
    print("⚠️ Existing vectorstore found – reusing it")
else:
    print("📦 Creating new vectorstore")


vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=VECTOR_DIR
)
'''

# =========================================================
# 6. VERIFICATION (VERY IMPORTANT)
# =========================================================

loader = WebBaseLoader(URLS)
documents = loader.load()

# Split text
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)
chunks = splitter.split_documents(documents)

# Store vectors
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=VECTOR_DIR
)

#vectorstore.persist()

print("✅ URLs scraped and indexed successfully")
