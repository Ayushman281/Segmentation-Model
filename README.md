# Image Segmentation Web Application

A web application that segments aerial/satellite images to identify buildings, roads, and water bodies using a pre-trained deep learning model.

## Features

- Upload images (TIFF, PNG, JPEG) up to 150MB
- Process images using a pre-trained segmentation model
- View and download segmented results
- Local deployment with option for cloud deployment

## Setup and Installation

### Prerequisites

- Python 3.8+
- Node.js 14+
- Pre-trained segmentation model weights

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/Mac: `source venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Place your model weights in the `weights` directory
6. Start the server:
   ```
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```
2. Install dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm start
   ```

## Usage

1. Access the application at http://localhost:3000
2. Upload an image using the file upload button
3. Wait for processing to complete
4. View the segmentation results
5. Download the segmented image if needed

## License

[MIT](https://choosealicense.com/licenses/mit/)
