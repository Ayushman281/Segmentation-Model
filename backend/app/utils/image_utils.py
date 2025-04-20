import os
import cv2
import numpy as np
from PIL import Image
import rasterio
from fastapi import HTTPException

def validate_image(file_path):
    """
    Validate that a file is an image and check its dimensions
    
    Args:
        file_path: Path to the image file
        
    Returns:
        True if the file is a valid image, False otherwise
    """
    try:
        # Check file extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() in ['.tif', '.tiff']:
            # Use rasterio for geospatial formats
            with rasterio.open(file_path) as src:
                if src.count < 1:
                    return False
        else:
            # Use PIL for standard image formats
            img = Image.open(file_path)
            img.verify()  # Verify it's an image
        return True
    except Exception:
        return False

def read_image_file(file_path):
    """
    Read an image file into a numpy array
    
    Args:
        file_path: Path to the image file
        
    Returns:
        A numpy array representing the image
    """
    try:
        # Check extension to determine how to load
        _, ext = os.path.splitext(file_path)
        if ext.lower() in ['.tif', '.tiff']:
            # Use rasterio for geospatial formats
            with rasterio.open(file_path) as src:
                if src.count == 1:  # Grayscale
                    image = src.read(1)
                else:  # Multi-band
                    # Read the first 3 bands (assuming RGB) or adjust as needed
                    bands_to_read = min(3, src.count)
                    image = np.zeros((src.height, src.width, bands_to_read), dtype=np.uint8)
                    for i in range(bands_to_read):
                        image[:, :, i] = src.read(i + 1)
        else:
            # Use OpenCV for standard image formats
            image = cv2.imread(file_path)
            if image is not None:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        return image
    except Exception as e:
        print(f"Error reading image: {str(e)}")
        return None

def save_output_image(image, file_path):
    """
    Save a processed image to disk
    
    Args:
        image: A numpy array representing the image
        file_path: Path where to save the image
    """
    try:
        # Convert from RGB to BGR for OpenCV
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Save the image
        cv2.imwrite(file_path, image)
    except Exception as e:
        raise Exception(f"Error saving output image: {str(e)}")

def create_overlay(original, mask, alpha=0.5):
    """
    Create an overlay of the original image and the segmentation mask
    
    Args:
        original: Original image as numpy array
        mask: Segmentation mask as numpy array
        alpha: Transparency level of the overlay
        
    Returns:
        A numpy array representing the overlay image
    """
    # Ensure mask is RGB if it's not already
    if len(mask.shape) == 2 or mask.shape[2] == 1:
        mask_rgb = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
    else:
        mask_rgb = mask
    
    # Resize mask if dimensions don't match
    if original.shape[:2] != mask_rgb.shape[:2]:
        mask_rgb = cv2.resize(mask_rgb, (original.shape[1], original.shape[0]))
    
    # Create overlay
    overlay = cv2.addWeighted(original, 1-alpha, mask_rgb, alpha, 0)
    
    return overlay
