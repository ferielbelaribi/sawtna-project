from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        return None
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_contents_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.GeneratedContent).filter(models.GeneratedContent.user_id == user_id).offset(skip).limit(limit).all()

def create_content(db: Session, content: schemas.ContentCreate):
    db_content = models.GeneratedContent(
        user_id=content.user_id,
        content_type=content.content_type,
        title=content.title,
        text=content.text,
        image_path=content.image_path,
        content_metadata=content.content_metadata
    )
    
    try:
        db.add(db_content)
        db.commit()
        db.refresh(db_content)
        return db_content
    except IntegrityError:
        db.rollback()
        return None