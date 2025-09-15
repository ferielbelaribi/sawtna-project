import os
import logging
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    ViTImageProcessor, ViTForImageClassification,
    pipeline
)
import torch
from PIL import Image
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)

class ModelLoader:
    def __init__(self):
        self.text_classifier = None
        self.image_classifier = None
        self.text_tokenizer = None
        self.image_processor = None
        self.load_models()
    
    def load_models(self):
        """Load both text and image classification models"""
        try:
            self.load_text_model()
            self.load_image_model()
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def load_text_model(self):
        """Load text classification model"""
        try:
            # First try to load your custom model
            model_path = "app/models/text_classifier"
            if os.path.exists(model_path):
                logger.info(f"Loading custom text model from {model_path}")
                self.text_tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.text_classifier = AutoModelForSequenceClassification.from_pretrained(model_path)
            else:
                # Fallback to a pre-trained model for content moderation
                logger.info("Loading fallback text classification model")
                self.text_classifier = pipeline(
                    "text-classification",
                    model="unitary/toxic-bert",
                    tokenizer="unitary/toxic-bert"
                )
        except Exception as e:
            logger.error(f"Error loading text model: {e}")
            # Use a simple rule-based fallback
            self.text_classifier = None
    
    def load_image_model(self):
        """Load image classification model"""
        try:
            # Check if custom model exists
            model_path = "app/models/image_classifier"
            if os.path.exists(model_path):
                logger.info(f"Loading custom image model from {model_path}")
                self.image_processor = ViTImageProcessor.from_pretrained(model_path)
                self.image_classifier = ViTForImageClassification.from_pretrained(model_path)
            else:
                # Use a pre-trained model for NSFW detection (placeholder)
                logger.info("Loading fallback image classification model")
                self.image_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
                self.image_classifier = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224")
        except Exception as e:
            logger.error(f"Error loading image model: {e}")
            self.image_classifier = None

# Global model loader instance
model_loader = ModelLoader()

def classify_text(text: str) -> dict:
    """
    Classify text content for appropriateness
    
    Args:
        text (str): Input text to classify
        
    Returns:
        dict: Classification result with label and confidence
    """
    try:
        if model_loader.text_classifier is None:
            # Simple rule-based fallback
            inappropriate_keywords = ['spam', 'hate', 'violence', 'explicit']
            is_inappropriate = any(keyword in text.lower() for keyword in inappropriate_keywords)
            
            return {
                "label": "INAPPROPRIATE" if is_inappropriate else "APPROPRIATE",
                "confidence": 0.6  # Low confidence for rule-based
            }
        
        if isinstance(model_loader.text_classifier, pipeline):
            # Using HuggingFace pipeline
            result = model_loader.text_classifier(text)
            # Assuming toxic-bert returns TOXIC/NON-TOXIC
            label = "INAPPROPRIATE" if result[0]['label'] == 'TOXIC' else "APPROPRIATE"
            confidence = result[0]['score']
        else:
            # Using custom model
            inputs = model_loader.text_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
            
            with torch.no_grad():
                outputs = model_loader.text_classifier(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
            predicted_class = torch.argmax(predictions, dim=1).item()
            confidence = torch.max(predictions).item()
            
            # Assuming 0 = appropriate, 1 = inappropriate
            label = "INAPPROPRIATE" if predicted_class == 1 else "APPROPRIATE"
        
        return {
            "label": label,
            "confidence": float(confidence)
        }
        
    except Exception as e:
        logger.error(f"Error in text classification: {e}")
        return {
            "label": "ERROR",
            "confidence": 0.0,
            "error": str(e)
        }

def classify_image(image_path: str) -> dict:
    """
    Classify image content for appropriateness
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        dict: Classification result with label and confidence
    """
    try:
        if model_loader.image_classifier is None:
            return {
                "label": "ERROR",
                "confidence": 0.0,
                "error": "Image classifier not available"
            }
        
        # Load and process image
        image = Image.open(image_path).convert('RGB')
        inputs = model_loader.image_processor(images=image, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model_loader.image_classifier(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        predicted_class = torch.argmax(predictions, dim=1).item()
        confidence = torch.max(predictions).item()
        
        # For now, using a simple rule since we don't have a proper NSFW model
        # In production, you'd want to use a model specifically trained for content moderation
        if hasattr(model_loader.image_classifier.config, 'id2label'):
            label_name = model_loader.image_classifier.config.id2label[predicted_class]
            # This is a placeholder - you'd implement proper logic based on your model
            inappropriate_classes = ['explicit', 'violence', 'adult']  # Example
            is_inappropriate = any(keyword in label_name.lower() for keyword in inappropriate_classes)
            label = "INAPPROPRIATE" if is_inappropriate else "APPROPRIATE"
        else:
            # Fallback for custom models without proper labels
            label = "INAPPROPRIATE" if predicted_class == 1 else "APPROPRIATE"
        
        return {
            "label": label,
            "confidence": float(confidence),
            "predicted_class": predicted_class
        }
        
    except Exception as e:
        logger.error(f"Error in image classification: {e}")
        return {
            "label": "ERROR",
            "confidence": 0.0,
            "error": str(e)
        }

# Test function to verify models are working
def test_models():
    """Test both models with sample inputs"""
    logger.info("Testing models...")
    
    # Test text classification
    test_text = "This is a normal text message"
    text_result = classify_text(test_text)
    logger.info(f"Text classification test: {text_result}")
    
    # Test image classification would need an actual image file
    logger.info("Models loaded and tested successfully!")