import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    "Content-Type": "multipart/form-data",
  },
});

/**
 * Upload an image file for segmentation
 *
 * @param {File} file - The image file to upload
 * @returns {Promise} - Promise with the response data
 */
export const uploadImage = async (file) => {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/segmentation", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      onUploadProgress: (progressEvent) => {
        // You can use this to track upload progress if needed
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        console.log(`Upload progress: ${percentCompleted}%`);
      },
    });

    return response.data;
  } catch (error) {
    console.error("Error uploading image:", error);

    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      throw new Error(error.response.data?.detail || "Server error occurred");
    } else if (error.request) {
      // The request was made but no response was received
      throw new Error(
        "No response from server. Please check your network connection."
      );
    } else {
      // Something happened in setting up the request that triggered an Error
      throw new Error(error.message);
    }
  }
};

/**
 * Get a specific segmentation result by job ID
 *
 * @param {string} jobId - The ID of the segmentation job
 * @returns {Promise} - Promise with the response data
 */
export const getSegmentationResult = async (jobId) => {
  try {
    const response = await api.get(`/segmentation/${jobId}`);
    return response.data;
  } catch (error) {
    console.error("Error getting segmentation result:", error);
    throw new Error(
      error.response?.data?.detail || "Failed to retrieve segmentation result"
    );
  }
};

export default api;
