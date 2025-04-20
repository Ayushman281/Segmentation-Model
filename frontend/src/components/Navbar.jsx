import React from "react";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import MapIcon from "@mui/icons-material/Map";

function Navbar() {
  return (
    <AppBar position="static">
      <Toolbar>
        <MapIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Image Segmentation Tool
        </Typography>
      </Toolbar>
    </AppBar>
  );
}

export default Navbar;
