from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from memory import add_to_memory,get_memory_context
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VECTOR_DIR = os.path.join(BASE_DIR, "vectorstore_routes")
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def dbsearch_answer(user_query):
    embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=OPENAI_API_KEY
        )

    db = Chroma(
        persist_directory=VECTOR_DIR,
        embedding_function=embeddings
    )

    results = db.similarity_search(user_query, k=3)
    return results

import random
import smtplib
from email.message import EmailMessage

def send_otp(user_email):
    # generate 6-digit OTP
    otp = random.randint(100000, 999999)
    sender_email = ''     # your email
    sender_password = ""     # app password (important)

    msg = EmailMessage()
    msg["Subject"] = "Your OTP Verification Code"
    msg["From"] = sender_email
    msg["To"] = user_email
    msg.set_content(f"Your OTP is: {otp}\n\nDo not share this OTP with anyone.")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

    return otp

#print(send_otp('rabadajit66@gmail.com'))