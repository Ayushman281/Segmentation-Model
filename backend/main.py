import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from app.routers import segmentation

# Load environment variables
load_dotenv()

# Create upload and output directories if they don't exist
upload_dir = os.getenv("UPLOAD_DIR", "uploads")
output_dir = os.getenv("OUTPUT_DIR", "output")
os.makedirs(upload_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

app = FastAPI(
    title="Image Segmentation API",
    description="API for segmenting images to detect buildings, roads, and water bodies",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(segmentation.router)

# Mount static files for serving uploaded and output images
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")
app.mount("/output", StaticFiles(directory=output_dir), name="output")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Image Segmentation API"}
