import React, { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Chip,
} from "@mui/material";
import GetAppIcon from "@mui/icons-material/GetApp";
import VisibilityIcon from "@mui/icons-material/Visibility";

function ImageDisplay({ result }) {
  const [loading, setLoading] = useState(false);

  if (!result) return null;

  const {
    job_id,
    original_filename,
    segmented_image_url,
    processing_time_seconds,
  } = result;

  const handleDownload = () => {
    setLoading(true);

    // Create a link to download the file and trigger it
    const link = document.createElement("a");
    link.href = `${process.env.REACT_APP_API_URL}${segmented_image_url}`;
    link.download = `segmented_${original_filename}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setLoading(false);
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
      <Typography variant="h5" gutterBottom component="div">
        Segmentation Results
      </Typography>

      <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
        <Chip
          label={`Processing time: ${processing_time_seconds.toFixed(2)}s`}
          variant="outlined"
          color="primary"
          size="small"
          sx={{ mr: 1 }}
        />
        <Chip label={`Job ID: ${job_id}`} variant="outlined" size="small" />
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Original filename: {original_filename}
        </Typography>
      </Box>

      <Box sx={{ my: 3, textAlign: "center" }}>
        <img
          src={`${process.env.REACT_APP_API_URL}${segmented_image_url}`}
          alt="Segmented Result"
          style={{
            maxWidth: "100%",
            maxHeight: "400px",
            border: "1px solid #ddd",
            borderRadius: "4px",
          }}
        />
      </Box>

      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          flexWrap: "wrap",
          mt: 2,
        }}
      >
        <Button
          variant="contained"
          color="primary"
          startIcon={<GetAppIcon />}
          onClick={handleDownload}
          disabled={loading}
        >
          {loading ? (
            <CircularProgress size={24} />
          ) : (
            "Download Segmented Image"
          )}
        </Button>

        <Button
          variant="outlined"
          startIcon={<VisibilityIcon />}
          href={`${process.env.REACT_APP_API_URL}${segmented_image_url}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          View Full Size
        </Button>
      </Box>
    </Paper>
  );
}

export default ImageDisplay;
