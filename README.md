- My whole project frontend(streamlit) and backend(fastapi) are located inside the chatbot folder
- to run the project
  download this folder and keep inside a env a install all requirements.txt
  to startbackend server run the main.py (uvicorn main:app --reload) it will satrt a sevrer on 8000 and before this give your openapi key inside .env located inside the backend folder
  to streamlit server run app.py located in frontend folder and use cmd to streamlit run  app.py in another terminal
- delete the database if you want to put newdata of yours

🚀 Tech Stack
🧠 AI / LLM

OpenAI GPT (Chat Model)
LangChain (Prompt handling & orchestration)

📚 RAG (Retrieval Augmented Generation)
Vector Database: FAISS
Embeddings: OpenAI Embeddings
Text Processing: LangChain Text Splitters

⚙️ Backend
FastAPI (API development)
Python

💾 Database
PostgreSQL (Chat history & sessions storage)
SQLAlchemy (ORM)

🧩 Memory & Context Handling
Custom Memory Storage
Session-based Chat Memory

📄 Document Processing
PDF Processing: pdfplumber
Website Data Extraction (if used)

🎨 Frontend / UI
Streamlit (Chat interface)

🔐 Authentication
JWT Authentication
User Session Management

☁️ Deployment / Tools
Uvicorn (ASGI server)
Git & GitHub (Version Control)
Virtual Environment (venv)

🏗️ Architecture
RAG-based Chatbot
Vector Search + LLM Response Generation
Memory-based Conversation Handling
   
