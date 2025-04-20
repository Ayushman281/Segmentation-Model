import os
import uuid
import time
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
from dotenv import load_dotenv
import cv2
import numpy as np

from app.services.segmentation_service import SegmentationService
from app.utils.image_utils import validate_image, read_image_file, save_output_image

# Load environment variables
load_dotenv()

router = APIRouter(
    prefix="/api/segmentation",
    tags=["segmentation"],
)

# Initialize segmentation service
segmentation_service = SegmentationService()

# Get allowed file extensions from environment
allowed_extensions = os.getenv("ALLOWED_EXTENSIONS", ".tif,.tiff,.png,.jpg,.jpeg").split(",")
max_file_size = int(os.getenv("MAX_FILE_SIZE", 157286400))  # 150MB default
upload_dir = os.getenv("UPLOAD_DIR", "uploads")
output_dir = os.getenv("OUTPUT_DIR", "output")

@router.post("/")
async def segment_image(file: UploadFile = File(...)):
    """
    Process an uploaded image and return segmentation results.
    
    Args:
        file: The image file to process
        
    Returns:
        JSON with the URL to the segmented image
    """
    # Generate a unique ID for this request
    job_id = str(uuid.uuid4())
    
    # Validate file extension
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail=f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}")

    # Check file size before processing
    contents = await file.read()
    if len(contents) > max_file_size:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {max_file_size / 1024 / 1024}MB")

    try:
        # Save the uploaded file
        upload_path = os.path.join(upload_dir, f"{job_id}_{file.filename}")
        with open(upload_path, "wb") as f:
            f.write(contents)
        
        # Load and validate the image
        image = read_image_file(upload_path)
        if image is None:
            raise HTTPException(status_code=400, detail="Failed to read image file")
        
        # Process the image
        start_time = time.time()
        mask = segmentation_service.process_image(image)
        colored_mask = segmentation_service.colorize_mask(mask)
        processing_time = time.time() - start_time
        
        # Save the segmented image
        output_filename = f"{job_id}_segmented.png"
        output_path = os.path.join(output_dir, output_filename)
        save_output_image(colored_mask, output_path)
        
        # Return response with link to the result
        return {
            "job_id": job_id,
            "original_filename": file.filename,
            "segmented_image_url": f"/output/{output_filename}",
            "processing_time_seconds": processing_time,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@router.get("/{job_id}")
async def get_segmentation_result(job_id: str):
    """
    Get the results of a previous segmentation job.
    
    Args:
        job_id: The unique identifier for the job
        
    Returns:
        The segmented image file
    """
    # Look for output file with the job ID
    for filename in os.listdir(output_dir):
        if filename.startswith(job_id):
            file_path = os.path.join(output_dir, filename)
            return FileResponse(file_path)
    
    raise HTTPException(status_code=404, detail="Segmentation result not found")
