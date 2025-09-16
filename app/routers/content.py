from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from fastapi.responses import JSONResponse, FileResponse
import os
import tempfile
import logging
import time
from typing import Dict, Any, List
from ..load_models import classify_text, classify_image
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import get_db
from .auth import get_current_user
from ..blood_detection import detect_blood
from ..image_generation import generate_image, generate_image_bytes
import shutil
import json
from pathlib import Path
import base64

# Configure logging
logger = logging.getLogger(__name__)

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

@router.get("/user-content", response_model=List[schemas.Content])
def get_user_content(
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db), 
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    """
    Get the current user's generated content
    """
    try:
        contents = crud.get_contents_by_user(db, current_user.id, skip=skip, limit=limit)
        return contents
    except Exception as e:
        logger.error(f"Error fetching user content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user content"
        )

@router.post("/classify-text", response_model=Dict[str, Any])
async def check_text(text: str = Body(..., embed=True)) -> JSONResponse:
    """
    Check if text content is appropriate
    """
    try:
        if not text or len(text.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text cannot be empty"
            )
        
        if len(text) > 5000:
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
                "label": result["label"],
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

@router.post("/classify-image", response_model=Dict[str, Any])
async def check_image(file: UploadFile = File(...)) -> JSONResponse:
    """
    Check if image content is appropriate
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
        
        if file_size > 10 * 1024 * 1024:
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
                "label": result["label"],
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
    Health check endpoint
    """
    try:
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
# Image generation - FIXED ENDPOINT
# -------------------------
@router.post("/generate-image")
async def generate_image_endpoint(prompt: str = Body(..., embed=True)):
    """
    Generate an image based on a text prompt and return as base64
    
    Args:
        prompt (str): Text description for image generation
        
    Returns:
        dict: Generated image data as base64
    """
    try:
        if not prompt or len(prompt.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt cannot be empty"
            )
        
        # Validate prompt length
        if len(prompt) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt is too long (max 1000 characters)"
            )
        
        logger.info(f"Generating image for prompt: {prompt}")
        
        # Generate image and get bytes directly
        image_bytes = generate_image_bytes(prompt.strip())
        
        # Validate that we actually got image data
        if not image_bytes or len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Image generation returned empty data"
            )
        
        # Verify it's a valid image by trying to open it
        try:
            from PIL import Image
            import io
            Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            logger.error(f"Generated image is invalid: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Generated image is invalid: {str(e)}"
            )
        
        # Convert to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        timestamp = int(time.time())
        filename = f"generated_image_{timestamp}.png"
        
        # Also save the image to disk for future reference
        os.makedirs("generated_images", exist_ok=True)
        filepath = os.path.join("generated_images", filename)
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        
        logger.info(f"Image successfully generated and saved as {filename}")
        
        return {
            "prompt": prompt,
            "filename": filename,
            "image_data": image_base64,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in image generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}"
        )

@router.post("/generate-image-base64")
async def generate_image_base64_endpoint(prompt: str = Body(..., embed=True)):
    """
    Generate an image and return as base64 encoded string
    """
    try:
        if not prompt or len(prompt.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt cannot be empty"
            )
        
        if len(prompt) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt is too long (max 1000 characters)"
            )
        
        logger.info(f"Generating base64 image for prompt: {prompt}")
        image_bytes = generate_image_bytes(prompt.strip())
        
        # Convert to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        timestamp = int(time.time())
        filename = f"generated_image_{timestamp}.png"
        
        return {
            "prompt": prompt,
            "filename": filename,
            "image_data": image_base64,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in base64 image generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}"
        )

@router.get("/generated-images/{filename}")
async def get_generated_image(filename: str):
    """
    Serve generated images
    """
    image_path = Path("generated_images") / filename
    
    if not image_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    return FileResponse(image_path)

# Debug endpoint
@router.post("/debug-generate-image")
async def debug_generate_image_endpoint(prompt: str = Body(..., embed=True)):
    """
    Debug endpoint to check what's happening with image generation
    """
    try:
        logger.info(f"Debug: Generating image for prompt: {prompt}")
        
        # Generate image and get bytes directly
        image_bytes = generate_image_bytes(prompt.strip())
        
        logger.info(f"Debug: Image bytes length: {len(image_bytes) if image_bytes else 0}")
        
        # Check if we got any data
        if not image_bytes or len(image_bytes) == 0:
            return {
                "status": "error",
                "message": "No image data received",
                "bytes_length": 0
            }
        
        # Try to validate the image
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_bytes))
            return {
                "status": "success",
                "message": f"Valid image: {img.format}, size: {img.size}",
                "bytes_length": len(image_bytes),
                "image_data": base64.b64encode(image_bytes).decode('utf-8')[:100] + "..."  # First 100 chars
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Invalid image: {str(e)}",
                "bytes_length": len(image_bytes),
                "image_data": base64.b64encode(image_bytes).decode('utf-8')[:100] + "..."  # First 100 chars
            }
            
    except Exception as e:
        logger.error(f"Debug error: {e}")
        return {
            "status": "error",
            "message": f"Exception: {str(e)}",
            "bytes_length": 0
        }
@router.post("/check-blood")
async def check_blood(file: UploadFile = File(...)):
    """
    Check for blood regions in an image
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
        content = await file.read()
        file_size = len(content)
        
        if file_size > 10 * 1024 * 1024:
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
        
        logger.info(f"Processing blood detection for image: {file.filename}")
        
        # Detect blood
        output_path, num_masks = detect_blood(temp_file_path)
        
        # If detection failed, return the original image
        if num_masks == 0 and output_path == temp_file_path:
            logger.warning("Blood detection may have failed, returning original image")
        
        # Get just the filename for the response
        output_filename = os.path.basename(output_path)
        
        return {
            "original_file": file.filename,
            "processed_file": f"processed_images/{output_filename}",
            "blood_regions_detected": num_masks,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in blood detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blood detection failed: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")

@router.get("/processed_images/{filename}")
async def get_processed_image(filename: str):
    """
    Serve processed blood detection images
    """
    image_path = Path("processed_images") / filename
    
    if not image_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processed image not found"
        )
    
    return FileResponse(image_path)