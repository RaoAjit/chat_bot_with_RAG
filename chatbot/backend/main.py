from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from company_data import answer
from pdf_emb import pdf_embedding,answer_from_pdf
from fastapi import FastAPI, UploadFile, File, Form
from urldata_emb import url_data_embeding,data_from_url
from utils import send_otp
from auth import create_token,get_current_user
from fastapi import HTTPException, Depends
from database import SessionLocal
from models import User, ChatSession,ChatMessage
from models import User
import models as models
from database import engine

app = FastAPI()
pdf_vector_cache = {}  
ulr_vector_cache={}
email_pass={}


models.Base.metadata.create_all(bind=engine)


class ChatRequest(BaseModel):
    message: str
    session_id:str


class UrlChatRequest(BaseModel):
    url: str
    question: str
    session_id:str


class registration_schema():
    email:str

class otp_shema(BaseModel):
    email:str

class login_schema(BaseModel):
    email:str
    otp:str 


@app.get('/ai')
def registration():
    pass

@app.post('/otp')
def otp(data: otp_shema):
    otp_code = send_otp(data.email)
    email_pass[data.email] = otp_code
    return {"success": True, "message": "OTP sent"}

@app.post('/login')
def login(data: login_schema):
    if data.email in email_pass and email_pass[data.email] == int(data.otp):

        db = SessionLocal()

        # Check user
        user = db.query(User).filter(User.email == data.email).first()

        if not user:
            user = User(email=data.email)
            db.add(user)
            db.commit()
            db.refresh(user)

        # ✅ Create new chat session
        new_session = ChatSession(user_id=user.id)
        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        token = create_token(data.email)

        db.close()

        return {
            "success": True,
            "access_token": token,
            "session_id": new_session.session_uuid   # ✅ send UUID
        }

    raise HTTPException(status_code=401, detail="Invalid OTP")

@app.post("/chat")
async def chat_bot(data: ChatRequest, user_email: str = Depends(get_current_user)):

    db = SessionLocal()

    # 🔍 Find session
    session = db.query(ChatSession).filter(
        ChatSession.session_uuid == data.session_id
    ).first()
    if session.title == 'New Chat':
        session.title = data.message
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # ✅ Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        sender="user",
        message=data.message
    )
    db.add(user_msg)

    # 🤖 Generate reply
    reply = answer(user_query=data.message)

    # ✅ Save bot reply
    bot_msg = ChatMessage(
        session_id=session.id,
        sender="bot",
        message=reply
    )
    db.add(bot_msg)

    db.commit()
    db.close()

    return {
        "user": user_email,
        "reply": reply
    }


@app.post("/pdf-chat")
async def chat_bot(file: UploadFile = File(...),
    question: str = Form(...),
    session_id: str = Form(...),
    user_email: str = Depends(get_current_user)):
    pdf_bytes = await file.read()
    filename = file.filename
    # If PDF not embedded yet
    if filename not in pdf_vector_cache:
        print("⚙️ Creating embeddings...")
        vector_store = pdf_embedding(pdf_bytes)
        pdf_vector_cache[filename] = vector_store
    else:
        print("♻️ Using cached embeddings...")
    
    vector_store = pdf_vector_cache[filename]
    db = SessionLocal()

    # 🔍 Find session
    session = db.query(ChatSession).filter(
        ChatSession.session_uuid == session_id
    ).first()
    if session.title == 'New Chat':
        session.title = question
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # ✅ Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        sender="user",
        message=question
    )
    db.add(user_msg)

    response = answer_from_pdf(question, vector_store)
    bot_msg = ChatMessage(
        session_id=session.id,
        sender="bot",
        message=response
    )
    db.add(bot_msg)

    db.commit()
    db.close()

    return {
             "user": user_email,
             "reply": response
             }


@app.post("/url-chat")
async def chat_bot(data:UrlChatRequest, user_email: str = Depends(get_current_user)):
    url=data.url
    question=data.question
    if data.url not in pdf_vector_cache:
        print("⚙️ Creating embeddings...")
        vector_store = url_data_embeding(url)
        pdf_vector_cache[url] = vector_store
    else:
        print("♻️ Using cached embeddings...")

    vector_store = pdf_vector_cache[url]
    
    db = SessionLocal()

    # 🔍 Find session
    session = db.query(ChatSession).filter(
        ChatSession.session_uuid == data.session_id
    ).first()
    if session.title == 'New Chat':
        session.title = data.question
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # ✅ Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        sender="user",
        message=data.question
    )
    db.add(user_msg)
    response = data_from_url(question, vector_store)
    bot_msg = ChatMessage(
        session_id=session.id,
        sender="bot",
        message=response
    )
    db.add(bot_msg)
    db.commit()
    db.close()

    return {"user": user_email,
             "reply": response
             }

@app.get("/chat-history/{session_uuid}")
def get_chat_history(session_uuid: str):

    db = SessionLocal()

    session = db.query(ChatSession).filter(
        ChatSession.session_uuid == session_uuid
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = [
        {
            "sender": msg.sender,
            "message": msg.message,
            "time": msg.created_at
        }
        for msg in session.messages
    ]

    db.close()

    return messages

@app.post("/new-session")
def create_session(user_email: str = Depends(get_current_user)):
    db = SessionLocal()

    user = db.query(User).filter(User.email == user_email).first()

    new_session = ChatSession(user_id=user.id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    db.close()

    return {"session_id": new_session.session_uuid}

@app.get("/my-history")
def get_my_history(user_email: str = Depends(get_current_user)):

    db = SessionLocal()

    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = []

    for session in user.sessions:
        session_data = {
            "session_uuid": session.session_uuid,
            "title": session.title,
        }

        result.append(session_data)

    db.close()

    return result
