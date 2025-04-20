import React, { useState } from "react";
import {
  Box,
  Button,
  Typography,
  LinearProgress,
  Paper,
  Alert,
  AlertTitle,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import BackupIcon from "@mui/icons-material/Backup";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";

import { uploadImage } from "../services/api";

const MAX_FILE_SIZE = process.env.REACT_APP_MAX_FILE_SIZE || 150000000; // 150MB default

function FileUpload({ onUploadComplete }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");

  // Handle file selection
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    // Reset states
    setError("");

    if (!selectedFile) return;

    // Check file size
    if (selectedFile.size > MAX_FILE_SIZE) {
      setError(
        `File size exceeds the maximum limit (${
          MAX_FILE_SIZE / 1024 / 1024
        }MB).`
      );
      return;
    }

    // Check file type
    const validExtensions = [".tif", ".tiff", ".png", ".jpg", ".jpeg"];
    const fileExt = selectedFile.name
      .substring(selectedFile.name.lastIndexOf("."))
      .toLowerCase();

    if (!validExtensions.includes(fileExt)) {
      setError(
        `Invalid file type. Accepted formats: ${validExtensions.join(", ")}`
      );
      return;
    }

    setFile(selectedFile);
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    try {
      setLoading(true);
      setProgress(0);

      // Simulated progress during upload
      const progressInterval = setInterval(() => {
        setProgress((prev) => (prev < 90 ? prev + 10 : prev));
      }, 500);

      // Upload the file
      const result = await uploadImage(file);

      // Clear interval and set progress to 100%
      clearInterval(progressInterval);
      setProgress(100);

      // Delay slightly before completing to show 100% progress
      setTimeout(() => {
        setLoading(false);
        if (onUploadComplete) {
          onUploadComplete(result);
        }
        setFile(null);
      }, 500);
    } catch (err) {
      setLoading(false);
      setError(err.message || "An error occurred during upload.");
      console.error("Upload error:", err);
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 4,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        backgroundColor: "#f9f9f9",
        border: "2px dashed #ccc",
        borderRadius: 2,
      }}
    >
      {error && (
        <Alert
          severity="error"
          sx={{ width: "100%", mb: 2 }}
          icon={<ErrorOutlineIcon fontSize="inherit" />}
        >
          <AlertTitle>Error</AlertTitle>
          {error}
        </Alert>
      )}

      <input
        accept=".tif,.tiff,.png,.jpg,.jpeg"
        style={{ display: "none" }}
        id="raised-button-file"
        type="file"
        onChange={handleFileChange}
        disabled={loading}
      />

      <label htmlFor="raised-button-file">
        <Button
          variant="outlined"
          component="span"
          startIcon={<CloudUploadIcon />}
          sx={{ mb: 2 }}
          disabled={loading}
        >
          Select Image File
        </Button>
      </label>

      {file && (
        <Box sx={{ width: "100%", my: 2 }}>
          <Typography variant="subtitle1" gutterBottom>
            Selected file: {file.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Size: {(file.size / 1024 / 1024).toFixed(2)} MB
          </Typography>
        </Box>
      )}

      {loading && (
        <Box sx={{ width: "100%", mt: 2 }}>
          <LinearProgress variant="determinate" value={progress} />
          <Typography
            variant="body2"
            color="text.secondary"
            align="center"
            sx={{ mt: 1 }}
          >
            {progress}% Uploaded
          </Typography>
        </Box>
      )}

      <Button
        variant="contained"
        color="primary"
        startIcon={<BackupIcon />}
        onClick={handleUpload}
        disabled={!file || loading}
        sx={{ mt: 2 }}
      >
        Upload and Process Image
      </Button>

      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ mt: 2, textAlign: "center" }}
      >
        Supported formats: TIF, TIFF, PNG, JPG, JPEG
        <br />
        Maximum file size: {MAX_FILE_SIZE / 1024 / 1024}MB
      </Typography>
    </Paper>
  );
}

export default FileUpload;
