import axios from "axios";

// Base API URL from environment variable or default to localhost
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api";

/**
 * Configured axios instance for making API requests
 * with extended timeout for processing large images
 */
const api = axios.create({
  baseURL: API_URL,
  timeout: 600000, // 10 minutes timeout for processing large images
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
      timeout: 600000, // 10 minutes timeout (matching the default)
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
        "No response from server. The segmentation is still processing. Please wait or try again in a few minutes."
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
    const response = await api.get(`/segmentation/${jobId}`, {
      timeout: 600000, // 2 minutes timeout for retrieving results
    });
    return response.data;
  } catch (error) {
    console.error("Error getting segmentation result:", error);
    throw new Error(
      error.response?.data?.detail || "Failed to retrieve segmentation result"
    );
  }
};

/**
 * Get statistics about the segmentation results
 *
 * @returns {Promise} - Promise with statistics data
 */
export const getSegmentationStats = async () => {
  try {
    const response = await api.get("/segmentation/stats");
    return response.data;
  } catch (error) {
    console.error("Error getting segmentation statistics:", error);
    throw new Error(
      error.response?.data?.detail ||
        "Failed to retrieve segmentation statistics"
    );
  }
};

/**
 * Cancel an ongoing segmentation job
 *
 * @param {string} jobId - The ID of the segmentation job to cancel
 * @returns {Promise} - Promise with the response data
 */
export const cancelSegmentation = async (jobId) => {
  try {
    const response = await api.post(`/segmentation/${jobId}/cancel`);
    return response.data;
  } catch (error) {
    console.error("Error canceling segmentation:", error);
    throw new Error(
      error.response?.data?.detail || "Failed to cancel segmentation"
    );
  }
};

export default api;
