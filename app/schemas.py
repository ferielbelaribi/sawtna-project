from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List

class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ContentBase(BaseModel):
    content_type: str
    title: Optional[str] = None
    text: Optional[str] = None
    image_path: Optional[str] = None
    content_metadata: Optional[Dict[str, Any]] = None

class ContentCreate(ContentBase):
    user_id: int

class Content(ContentBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True