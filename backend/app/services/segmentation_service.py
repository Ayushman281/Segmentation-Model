import os
from app.models.segmentation import SegmentationModel

class SegmentationService:
    """Service for handling image segmentation tasks"""
    
    def __init__(self):
        """Initialize the segmentation service"""
        self.model = SegmentationModel()
        
    def process_image(self, image):
        """
        Process an image using the segmentation model
        
        Args:
            image: A numpy array representing the image
            
        Returns:
            A numpy array representing the segmentation mask
        """
        try:
            # Run the model prediction
            mask = self.model.predict(image)
            return mask
        except Exception as e:
            raise Exception(f"Error during image segmentation: {str(e)}")
    
    def colorize_mask(self, mask):
        """
        Convert a class mask to a colored visualization
        
        Args:
            mask: A numpy array containing class indices
            
        Returns:
            A numpy array representing the colored segmentation mask
        """
        return self.model.colorize_mask(mask)
