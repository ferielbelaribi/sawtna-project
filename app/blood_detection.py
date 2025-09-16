import cv2
import torch
import numpy as np
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Initialize SAM model (singleton pattern)
_sam_model = None
_mask_generator = None

def initialize_sam_model():
    """Initialize the SAM model once"""
    global _sam_model, _mask_generator
    
    if _sam_model is None:
        try:
            # Use absolute path to avoid issues
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sam_checkpoint = os.path.join(current_dir, "models", "sam_vit_b_01ec64.pth")
            
            # Check if model file exists
            if not os.path.exists(sam_checkpoint):
                logger.error(f"SAM model not found at: {sam_checkpoint}")
                # Try to find the model with a different name
                model_files = [f for f in os.listdir(os.path.join(current_dir, "models")) 
                             if f.endswith('.pth')]
                if model_files:
                    sam_checkpoint = os.path.join(current_dir, "models", model_files[0])
                    logger.info(f"Using alternative model: {sam_checkpoint}")
                else:
                    raise FileNotFoundError("No SAM model files found in models directory")
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading SAM model on device: {device}")
            
            _sam_model = sam_model_registry["vit_b"](checkpoint=sam_checkpoint)
            _sam_model.to(device=device)
            _mask_generator = SamAutomaticMaskGenerator(_sam_model)
            
            logger.info("SAM model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading SAM model: {e}")
            raise

def is_blood_region(image_rgb, mask, red_threshold=0.35):
    """Check if the masked region has dominant red."""
    try:
        region = image_rgb[mask.astype(bool)]
        if region.size == 0:
            return False
        mean_color = np.mean(region, axis=0)  # [R,G,B]
        red_ratio = mean_color[0] / (mean_color.sum() + 1e-6)
        return red_ratio > red_threshold
    except Exception as e:
        logger.warning(f"Error in blood region detection: {e}")
        return False

def detect_blood(image_path):
    """Return an image with red regions detected and processed."""
    # Initialize model if not already done
    if _sam_model is None:
        initialize_sam_model()
    
    try:
        # Read and validate image
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Generate masks
        logger.info("Generating masks...")
        masks = _mask_generator.generate(image_rgb)
        logger.info(f"Generated {len(masks)} masks")
        
        # Filter masks with dominant red
        blood_masks = [m["segmentation"] for m in masks if is_blood_region(image_rgb, m["segmentation"])]
        logger.info(f"Found {len(blood_masks)} blood regions")
        
        # Create output image with blood regions highlighted
        output = image.copy()
        
        # Highlight blood regions with red overlay instead of blur
        for mask in blood_masks:
            try:
                # Create red overlay for blood regions
                red_overlay = np.zeros_like(image)
                red_overlay[mask == 1] = [0, 0, 255]  # Red color in BGR
                
                # Blend with original image
                alpha = 0.6  # Transparency
                output[mask == 1] = cv2.addWeighted(image[mask == 1], 1 - alpha, 
                                                   red_overlay[mask == 1], alpha, 0)
            except Exception as e:
                logger.warning(f"Error processing mask: {e}")
                continue
        
        # Save processed image
        output_dir = "processed_images"
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.basename(image_path)
        name, ext = os.path.splitext(base_name)
        output_filename = f"{name}_blood_detected{ext}"
        output_path = os.path.join(output_dir, output_filename)
        
        cv2.imwrite(output_path, output)
        
        return output_path, len(blood_masks)
        
    except Exception as e:
        logger.error(f"Error in blood detection: {e}")
        # Return original image path and 0 detections
        return image_path, 0