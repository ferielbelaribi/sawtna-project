import requests
from PIL import Image
from io import BytesIO
import urllib.parse
import time
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

def generate_image(prompt, width=512, height=512, seed=None):
    """
    Generate an image using pollinations.ai API
    
    Args:
        prompt (str): Text description for image generation
        width (int): Image width
        height (int): Image height
        seed (int): Random seed for reproducibility
        
    Returns:
        str: Filename of the generated image
    """
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
        if seed:
            url += f"&seed={seed}"
        
        logger.info(f"Generating image for prompt: {prompt}")
        response = requests.get(url, timeout=120)  # Increased timeout
        response.raise_for_status()
        
        # Create generated_images directory if it doesn't exist
        os.makedirs("generated_images", exist_ok=True)
        
        img = Image.open(BytesIO(response.content))
        timestamp = int(time.time())
        filename = f"generated_image_{timestamp}.png"
        filepath = os.path.join("generated_images", filename)
        
        img.save(filepath)
        logger.info(f"Image saved to: {filepath}")
        
        return filename
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error in image generation: {e}")
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        logger.error(f"Error in image generation: {e}")
        raise Exception(f"Image generation failed: {str(e)}")

def generate_image_bytes(prompt, width=512, height=512, seed=None):
    """
    Generate image and return as bytes
    
    Args:
        prompt (str): Text description for image generation
        width (int): Image width
        height (int): Image height
        seed (int): Random seed for reproducibility
        
    Returns:
        bytes: Image data as bytes
    """
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
        if seed:
            url += f"&seed={seed}"
        
        logger.info(f"Generating image bytes for prompt: {prompt}")
        response = requests.get(url, timeout=120)
        response.raise_for_status()
        
        return response.content
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error in image generation: {e}")
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        logger.error(f"Error in image generation: {e}")
        raise Exception(f"Image generation failed: {str(e)}")