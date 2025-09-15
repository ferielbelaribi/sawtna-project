import cv2
import torch
import numpy as np
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

# Load SAM model (once)
sam_checkpoint = "app\models\effect.pth"
device = "cuda" if torch.cuda.is_available() else "cpu"

sam = sam_model_registry["vit_b"](checkpoint=sam_checkpoint)
sam.to(device=device)

mask_generator = SamAutomaticMaskGenerator(sam)

def is_blood_region(image_rgb, mask, red_threshold=0.35):
    """Check if the masked region has dominant red."""
    region = image_rgb[mask.astype(bool)]
    if region.size == 0:
        return False
    mean_color = np.mean(region, axis=0)  # [R,G,B]
    red_ratio = mean_color[0] / (mean_color.sum() + 1e-6)
    return red_ratio > red_threshold

def detect_blood(image_path):
    """Return an image with red regions blurred."""
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    masks = mask_generator.generate(image_rgb)

    # Filter masks with dominant red
    blood_masks = [m["segmentation"] for m in masks if is_blood_region(image_rgb, m["segmentation"])]

    # Apply blur
    output = image.copy()
    for mask in blood_masks:
        blurred = cv2.GaussianBlur(image, (51, 51), 0)
        output[mask == 1] = blurred[mask == 1]

    # Save or return
    output_path = image_path.replace(".", "_blood_blurred.")
    cv2.imwrite(output_path, output)
    return output_path, len(blood_masks)
