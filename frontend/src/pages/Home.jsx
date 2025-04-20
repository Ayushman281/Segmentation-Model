import React, { useState } from "react";
import { Box, Typography, Paper, Grid, Divider } from "@mui/material";
import FileUpload from "../components/FileUpload";
import ImageDisplay from "../components/ImageDisplay";

function Home() {
  const [result, setResult] = useState(null);

  const handleUploadComplete = (uploadResult) => {
    setResult(uploadResult);
  };

  return (
    <Box>
      <Paper elevation={0} sx={{ p: 2, mb: 3, bgcolor: "background.paper" }}>
        <Typography variant="h4" gutterBottom>
          Image Segmentation Tool
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Upload an aerial or satellite image to segment buildings, roads, and
          water bodies using our deep learning model.
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <FileUpload onUploadComplete={handleUploadComplete} />
        </Grid>

        <Grid item xs={12} md={6}>
          {result ? (
            <ImageDisplay result={result} />
          ) : (
            <Paper
              elevation={3}
              sx={{
                p: 3,
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                minHeight: "200px",
                bgcolor: "#f9f9f9",
              }}
            >
              <Typography variant="h6" color="text.secondary" align="center">
                No Results Yet
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center">
                Upload an image to see the segmentation results here
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>

      <Divider sx={{ my: 4 }} />

      <Paper elevation={0} sx={{ p: 3, bgcolor: "background.paper" }}>
        <Typography variant="h5" gutterBottom>
          About This Tool
        </Typography>
        <Typography variant="body1" paragraph>
          This tool uses a deep learning model to segment different features in
          aerial and satellite imagery. The model has been trained to recognize
          three main categories:
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Paper elevation={1} sx={{ p: 2, bgcolor: "#fff8f8" }}>
              <Typography variant="h6" sx={{ color: "#d32f2f" }}>
                Buildings
              </Typography>
              <Typography variant="body2">
                Structures like houses, commercial buildings, and other man-made
                constructions.
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper elevation={1} sx={{ p: 2, bgcolor: "#f8fff8" }}>
              <Typography variant="h6" sx={{ color: "#388e3c" }}>
                Roads
              </Typography>
              <Typography variant="body2">
                Highways, streets, paths, and other transportation
                infrastructure.
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper elevation={1} sx={{ p: 2, bgcolor: "#f8f8ff" }}>
              <Typography variant="h6" sx={{ color: "#1976d2" }}>
                Water Bodies
              </Typography>
              <Typography variant="body2">
                Lakes, rivers, oceans, pools, and other water features.
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
}

export default Home;
