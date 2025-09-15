from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
import os
import tempfile
import logging
from typing import Dict, Any
from ..load_models import classify_text, classify_image
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db
from .auth import get_current_user
from ..blood_detection import detect_blood
from ..image_generation import generate_image, generate_image_bytes
import shutil
# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/content", tags=["content"])











router = APIRouter(prefix="/content", tags=["content"])

@router.post("/", response_model=schemas.Content)
def create_content(content: schemas.ContentCreate, db: Session = Depends(get_db), current_user: schemas.UserResponse = Depends(get_current_user)):
#     # Set the user_id to the current authenticated user
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



@router.post("/check_text", response_model=Dict[str, Any])
async def check_text(text: str) -> JSONResponse:
    """
    Check if text content is appropriate
    
    Args:
        text (str): Text content to analyze
        
    Returns:
        JSONResponse: Classification result with text, label, and confidence
    """
    try:
        if not text or len(text.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )
        
        if len(text) > 5000:  # Reasonable limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text is too long (max 5000 characters)"
            )
        
        logger.info(f"Classifying text of length: {len(text)}")
        result = classify_text(text.strip())
        
        if result.get("label") == "ERROR":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Classification failed: {result.get('error', 'Unknown error')}"
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "text": text,
                "classification": result["label"],
                "confidence": result["confidence"],
                "status": "success"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in text classification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during text classification"
        )


@router.post("/check-image", response_model=Dict[str, Any])
async def check_image(file: UploadFile = File(...)) -> JSONResponse:
    """
    Check if image content is appropriate
    
    Args:
        file (UploadFile): Image file to analyze
        
    Returns:
        JSONResponse: Classification result with filename, label, and confidence
    """
    temp_file_path = None
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Check file size (10MB limit)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size too large (max 10MB)"
            )
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(content)
        
        logger.info(f"Processing image: {file.filename}, size: {file_size} bytes")
        
        # Classify image
        result = classify_image(temp_file_path)
        
        if result.get("label") == "ERROR":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Classification failed: {result.get('error', 'Unknown error')}"
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "filename": file.filename,
                "file_size": file_size,
                "content_type": file.content_type,
                "classification": result["label"],
                "confidence": result["confidence"],
                "status": "success"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in image classification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during image classification"
        )
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")


@router.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint to verify the content classification service is working
    """
    try:
        # Test text classification with a simple message
        test_result = classify_text("Hello world")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "text_classifier": "working" if test_result.get("label") != "ERROR" else "error",
                "image_classifier": "loaded",
                "message": "Content classification service is operational"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "message": "Content classification service is experiencing issues"
            }
        )
    
# -------------------------
# Blood detection / segmentation
# -------------------------
@router.post("/check-blood")
async def check_blood(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    output_path, num_masks = detect_blood(file_path)
    return {"original_file": file.filename, "processed_file": output_path, "blood_regions_detected": num_masks}

# -------------------------
# Image generation
# -------------------------
@router.post("/generate-image")
def generate_image_endpoint(prompt: str):
    filename = generate_image(prompt)
    return {"prompt": prompt, "generated_file": filename}