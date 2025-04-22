import os
from app.models.segmentation import SegmentationModel

class SegmentationService:
    def __init__(self):

        self.model = SegmentationModel()
        
    def process_image(self, image):

        try:
            # Run the model prediction
            mask = self.model.predict(image)
            return mask
        except Exception as e:
            raise Exception(f"Error during image segmentation: {str(e)}")
    def colorize_mask(self, mask):

        return self.model.colorize_mask(mask)
