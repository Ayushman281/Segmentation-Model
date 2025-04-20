import torch
import torch.nn as nn
import numpy as np

# For ONNX export
import onnx

# For ONNX to TensorFlow conversion
import onnx
from onnx_tf.backend import prepare

# For TensorFlow and H5 saving
import tensorflow as tf
import os

# ---- 1. Define your PyTorch model architecture here ----
class MySegmentationModel(nn.Module):
    def __init__(self, num_classes=4):
        super(MySegmentationModel, self).__init__()
        self.model = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, num_classes, kernel_size=1)
        )

    def forward(self, x):
        return self.model(x)

# ---- 2. Load your PyTorch model weights ----
def load_pytorch_model(pth_path, num_classes=4):
    model = MySegmentationModel(num_classes)
    model.load_state_dict(torch.load(pth_path, map_location='cpu'))
    model.eval()
    return model

# ---- 3. Export to ONNX ----
def export_to_onnx(model, onnx_path):
    dummy_input = torch.randn(1, 3, 256, 256)  # Change shape as per your requirement
    torch.onnx.export(model, dummy_input, onnx_path, opset_version=11, input_names=['input'], output_names=['output'])
    print(f"ONNX model saved at {onnx_path}")

# ---- 4. Convert ONNX to TensorFlow ----
def onnx_to_tf(onnx_path, tf_model_dir):
    onnx_model = onnx.load(onnx_path)
    tf_rep = prepare(onnx_model)
    tf_rep.export_graph(tf_model_dir)
    print(f"TensorFlow model saved at {tf_model_dir}")

# ---- 5. Convert TensorFlow SavedModel to Keras H5 ----
def tf_savedmodel_to_h5(tf_model_dir, h5_path):
    model = tf.keras.models.load_model(tf_model_dir)
    model.save(h5_path)
    print(f"Keras H5 model saved at {h5_path}")

# ---- 6. Main function tying it all together ----
def convert_pth_to_h5(pth_path, onnx_path, tf_model_dir, h5_path, num_classes=4):
    # Step 1 & 2: Load PyTorch model and weights
    model = load_pytorch_model(pth_path, num_classes)
    # Step 3: Export to ONNX
    export_to_onnx(model, onnx_path)
    # Step 4: ONNX to TensorFlow
    onnx_to_tf(onnx_path, tf_model_dir)
    # Step 5: TensorFlow SavedModel to Keras H5
    tf_savedmodel_to_h5(tf_model_dir, h5_path)

if __name__ == "__main__":
    # Set your paths here
    PTH_PATH = "D:/College/Projects/Segmentation Model/backend/app/models/weights/combined_model_best.pth"
    ONNX_PATH = "D:/College/Projects/Segmentation Model/model_weight_conv/model.onnx"
    TF_MODEL_DIR = "app/models/weights/tf_model"
    H5_PATH = "app/models/weights/model.h5"

    convert_pth_to_h5(PTH_PATH, ONNX_PATH, TF_MODEL_DIR, H5_PATH, num_classes=4)

    print("Conversion complete!")