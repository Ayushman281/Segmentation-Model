import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import backend as K
from dotenv import load_dotenv
import cv2

load_dotenv()

# Define the custom metric function
def jaccard_coef(y_true, y_pred):
    """
    Jaccard coefficient metric (IoU) for multi-class segmentation
    """
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = K.sum(y_true_f * y_pred_f)
    return (intersection + 1.0) / (K.sum(y_true_f) + K.sum(y_pred_f) - intersection + 1.0)

class SegmentationModel:
    def __init__(self):
        self.model_path = os.getenv("MODEL_PATH", "app/models/weights/combined_model_best.h5")
        self.model = self._load_model()
        self.classes = ["background", "building", "road", "water"]
        self.num_classes = len(self.classes)

    def _load_model(self):
        """Load the pretrained TensorFlow segmentation model."""
        try:
            # Create the directory for weights if it doesn't exist
            weights_dir = os.path.dirname(self.model_path)
            if not os.path.exists(weights_dir):
                os.makedirs(weights_dir)
                print(f"Created weights directory: {weights_dir}")
            
            # Load the model from H5 file with custom metrics
            custom_objects = {'jaccard_coef': jaccard_coef}
            with tf.keras.utils.custom_object_scope(custom_objects):
                model = tf.keras.models.load_model(self.model_path)
                
            print(f"Model loaded successfully from {self.model_path}")
            return model
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return None

    def preprocess(self, image):
        """Preprocess the image for the TensorFlow model."""
        # Store original dimensions for later resizing of the output
        original_height, original_width = image.shape[:2]
        self.original_dimensions = (original_height, original_width)
    
        # Convert grayscale to RGB if needed
        if len(image.shape) == 2:
            image = np.stack((image,)*3, axis=-1)
        elif image.shape[2] == 1:
            image = np.concatenate((image,)*3, axis=-1)
    
        # Resize image to the model's expected input size (256x256)
        resized_image = cv2.resize(image, (256, 256))
    
        # Normalize the image
        resized_image = resized_image / 255.0
    
        # Add batch dimension
        input_tensor = np.expand_dims(resized_image, axis=0)
    
        return input_tensor

    def predict(self, image):
        """Run inference on the image and return segmentation mask."""
        if self.model is None:
         raise ValueError("Model not loaded correctly")
    
        # Preprocess the image
        input_tensor = self.preprocess(image)
    
        # Run inference
        output = self.model.predict(input_tensor)
    
        # Post-process to get segmentation mask (assuming output has shape [batch, height, width, classes])
        mask = np.argmax(output[0], axis=-1)
    
        # Resize mask back to original image dimensions
        original_height, original_width = self.original_dimensions
        mask = cv2.resize(mask.astype(np.uint8), (original_width, original_height), 
                      interpolation=cv2.INTER_NEAREST)
    
        return mask

    def colorize_mask(self, mask):
        """Convert segmentation mask to a colored image."""
        # Define colors for each class (RGB)
        colors = [
            [0, 0, 0],        # background - black
            [255, 0, 0],      # building - red
            [0, 255, 0],      # road - green
            [0, 0, 255],      # water - blue
        ]
        
        # Create RGB color image
        rgb_mask = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
        
        for i, color in enumerate(colors):
            rgb_mask[mask == i] = color
            
        return rgb_mask