import numpy as np
import cv2
import os
import torch
from PIL import Image
import matplotlib.pyplot as plt
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

class SegmentationModel:
    def __init__(self):
        
        # Define paths
        model_dir = os.path.dirname(__file__)
        checkpoint_name = "sam_vit_h_4b8939.pth"
        self.checkpoint_path = os.path.join(model_dir, checkpoint_name)
        
        # Check if model exists
        if not os.path.exists(self.checkpoint_path):
            print(f"Model weight not found at {self.checkpoint_path}")
            print(f"Attempting to look in other common locations...")
            
            # Try other common locations
            common_paths = [
                os.path.join(os.getcwd(), checkpoint_name),
                os.path.join(os.path.expanduser("~"), ".cache", "torch", "hub", "checkpoints", checkpoint_name),
                os.path.join(".", checkpoint_name)
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    self.checkpoint_path = path
                    print(f"Found model at: {path}")
                    break
            
        # Set device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load model
        self.model_type = "vit_h"  # Options: vit_h (largest), vit_l, vit_b (smallest)
        self.sam = sam_model_registry[self.model_type](checkpoint=self.checkpoint_path)
        self.sam.to(device=self.device)
        
        # Create mask generator with parameters optimized for satellite imagery
        self.mask_generator = SamAutomaticMaskGenerator(
            model=self.sam,
            points_per_side=32,
            pred_iou_thresh=0.86,
            stability_score_thresh=0.92,
            crop_n_layers=1,
            crop_n_points_downscale_factor=2,
            min_mask_region_area=100,
        )
        self.colors = {'building': [255, 255, 255], 'road': [255, 255, 255], 'water': [255, 255, 255],'other': [255, 255, 255]}
        
        # Maximum image dimension for processing
        self.max_image_dim = 1024  # Adjust based on your system's memory

    def preprocess_image(self, img):
        """
        Preprocess the input image for SAM.
        """
        # Make a copy to avoid modifying the original
        img_copy = img.copy()
        
        # Convert to RGB if needed
        if len(img_copy.shape) == 2:
            img_copy = cv2.cvtColor(img_copy, cv2.COLOR_GRAY2RGB)
        elif img_copy.shape[2] == 4:  # with alpha channel
            img_copy = cv2.cvtColor(img_copy, cv2.COLOR_RGBA2RGB)
        elif img_copy.shape[2] == 3 and img_copy.dtype == np.uint8:
            # Check if image is in BGR (OpenCV default) and convert to RGB
            img_copy = cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB)
            
        return img_copy
        
    def resize_if_needed(self, img):
        """
        Resize image if it's too large for memory-efficient processing.
        Returns resized image and scale factors.
        """
        height, width = img.shape[:2]
        print(f"Original image size: {width}x{height}")
        
        # Check if image needs resizing
        max_dim = max(height, width)
        if max_dim > self.max_image_dim:
            scale = self.max_image_dim / max_dim
            new_width = int(width * scale)
            new_height = int(height * scale)
            resized_img = cv2.resize(img, (new_width, new_height))
            print(f"Resized image to: {new_width}x{new_height}")
            return resized_img, (scale, scale)
        
        return img, (1.0, 1.0)
    
    def classify_segment(self, image, mask):
        """
        Simple heuristic to classify segments as building, road, or water
        based on color and shape properties.
        """
        # Create a mask image for OpenCV functions
        mask_img = mask.astype(np.uint8) * 255
        
        # Apply mask to original image
        masked_img = cv2.bitwise_and(image, image, mask=(mask_img > 0).astype(np.uint8))
        
        # Calculate mean color of the segment (excluding zeros)
        non_zero_pixels = (mask_img > 0).astype(np.uint8)
        if np.sum(non_zero_pixels) == 0:
            return 'other'  # Empty mask
        
        mean_val = cv2.mean(image, mask=non_zero_pixels)[:3]  # RGB means
        
        # Find contours for shape analysis
        contours, _ = cv2.findContours(mask_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return 'other'  # No contours found
        
        # Get the largest contour for shape analysis
        largest_contour = max(contours, key=cv2.contourArea)
        contour_area = cv2.contourArea(largest_contour)
        
        if contour_area < 10:
            return 'other'  # Too small to classify
        
        # Calculate shape metrics
        perimeter = cv2.arcLength(largest_contour, True)
        if perimeter == 0:
            return 'other'
            
        circularity = 4 * np.pi * contour_area / (perimeter * perimeter + 1e-10)
        
        # Get bounding rectangle to calculate aspect ratio
        x, y, w, h = cv2.boundingRect(largest_contour)
        aspect_ratio = max(w, h) / (min(w, h) + 1e-5)
        
        # Check for water bodies (typically blue/dark)
        # In RGB: Blue channel (idx 2) higher than others
        if (mean_val[2] > mean_val[0] + 10 and 
            mean_val[2] > mean_val[1] + 10 and 
            circularity > 0.3):
            return 'water'
        
        # Check for roads (grayish, elongated shape)
        # In RGB: All channels similar (gray) and high aspect ratio
        if (aspect_ratio > 3.0 and
            abs(mean_val[0] - mean_val[1]) < 20 and
            abs(mean_val[1] - mean_val[2]) < 20):
            return 'road'
        
        # Buildings often have regular shapes and distinct colors from background
        if (0.2 < circularity < 0.8 and
            aspect_ratio < 3.0):
            return 'building'
        
        # Default classification
        return 'other'
    
    def predict(self, img):
        try:
            # Get original image dimensions for later upscaling
            orig_height, orig_width = img.shape[:2]
            
            # Preprocess image
            processed_img = self.preprocess_image(img)
            
            # Resize image if needed to prevent memory errors
            resized_img, scale_factors = self.resize_if_needed(processed_img)
            height, width = resized_img.shape[:2]
            
            # Generate masks
            print("Generating segmentation masks...")
            masks = self.mask_generator.generate(resized_img)
            print(f"Generated {len(masks)} masks")
            
            # Create empty RGB mask for the resized dimensions
            segmentation_map = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Sort masks by area (largest first to handle overlaps better)
            sorted_masks = sorted(masks, key=lambda x: x['area'], reverse=True)
            
            # Process each mask - limit to 30 largest masks for memory and performance
            for i, mask_data in enumerate(sorted_masks[:30]):
                binary_mask = mask_data['segmentation']
                
                # Classify segment based on visual features
                segment_class = self.classify_segment(resized_img, binary_mask)
                
                # Get color for this class
                color = self.colors[segment_class]
                
                # Only update empty areas of the segmentation map
                empty_pixels = (segmentation_map == 0).all(axis=2)
                masked_areas = binary_mask & empty_pixels
                
                # Apply color to the mask
                for c in range(3):
                    segmentation_map[:,:,c] = np.where(
                        masked_areas,
                        color[c],
                        segmentation_map[:,:,c]
                    )
            
            # Resize segmentation map back to original dimensions if it was resized
            if scale_factors[0] != 1.0:
                segmentation_map = cv2.resize(
                    segmentation_map, 
                    (orig_width, orig_height),
                    interpolation=cv2.INTER_NEAREST  # Preserve mask colors
                )
            
            return segmentation_map
            
        except Exception as e:
            print(f"Error in segmentation: {str(e)}")
            # Return empty segmentation map on error
            return np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    
    def colorize_mask(self, mask):
        """
        This function is kept for compatibility with existing code,
        but the masks are already colorized in the predict function.
        """
        return mask
