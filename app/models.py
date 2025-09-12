from sqlalchemy import Column, Integer, String, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean)
    created_at = Column(TIMESTAMP(timezone=False), server_default=func.now())  # ✅ Correct

class GeneratedContent(Base):
    __tablename__ = "generatedcontent"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content_type = Column(String(50), nullable=False)
    title = Column(String(255))
    text = Column(Text)
    image_path = Column(Text)
    content_metadata = Column(JSONB, name="metadata")
    created_at = Column(TIMESTAMP, server_default=func.now())  # ✅ Fixed - use func.now() instead of string