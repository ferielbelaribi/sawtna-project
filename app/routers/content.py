from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db
from .auth import get_current_user

router = APIRouter(prefix="/content", tags=["content"])

@router.post("/", response_model=schemas.Content)
def create_content(content: schemas.ContentCreate, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    # Set the user_id to the current authenticated user
    content.user_id = current_user.id
    db_content = crud.create_content(db, content)
    if not db_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating content"
        )
    return db_content

@router.get("/my-content", response_model=List[schemas.Content])
def read_user_contents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
    contents = crud.get_contents_by_user(db, current_user.id, skip=skip, limit=limit)
    return contents