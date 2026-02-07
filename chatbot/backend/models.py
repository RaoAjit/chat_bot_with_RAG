import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from database import Base


# ---------------- USER TABLE ----------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)

    # One user -> Many sessions
    sessions = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete"
    )


# ---------------- SESSION TABLE ----------------
class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)

    # Public session ID (UUID string)
    session_uuid = Column(
        String,
        unique=True,
        index=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False
    )

    user_id = Column(Integer, ForeignKey("users.id"))

    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="sessions")

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete"
    )


# ---------------- MESSAGE TABLE ----------------
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(Integer, ForeignKey("chat_sessions.id"))

    sender = Column(String)  # "user" or "bot"
    message = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    session = relationship("ChatSession", back_populates="messages")
