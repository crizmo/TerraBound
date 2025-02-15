# TerraBound

TerraBound is a dynamic web mapping application developed using React, Vite, and React-Leaflet, styled with Tailwind CSS and Shadcn. It allows users to create, edit, and manage geographical features such as points, lines, and areas, and integrates functionalities for enhanced data interaction and documentation.

## Table of Contents
- [Hackofiesta 6.0 - AISpire UP Hackathon](#hackofiesta-60---aispire-up-hackathon)
- [Features](#features)
- [How the Process Works](#how-the-process-works)
- [MapComponent Overview](#mapcomponent-overview)
- [AI Model Integration](#ai-model-integration)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)

## Hackofiesta 6.0 - AISpire UP Hackathon

### Problem Statement

**Title:** AI-based application for Auto-Measurement of Land Area

**Description:**
An AI-based application for auto-measurement of land area utilizes advanced technologies like satellite imagery, GPS, and machine learning algorithms to accurately measure and map land parcels. Traditionally, land measurement has been a manual process, often prone to errors and delays.

The AI application automates this process by analyzing geospatial data and identifying land boundaries with high precision. By using real-time satellite data and GPS coordinates, it can provide instant measurements of land area without the need for physical surveys.

**Department:** Board of Revenue  
**Sector:** Land Administration and Revenue

## Features

- **Create Geographic Features**: Add points, lines, and areas to the map.
- **Text Mode**: Attach text to features; view text in popups by hovering.
- **Edit and Delete**: Modify or remove existing map features.
- **Sidebar with Details**: View feature details in a sidebar, including unique IDs, types, text, and coordinates.
- **GEOJSON Export**: Copy feature details in GEOJSON format directly from the sidebar.
- **Search Functionality**: Quickly find features listed in the sidebar.
- **Segmentation**: Segment satellite images and visualize the results on the map.

## How the Process Works

### 1. Creating a Bounding Box
- The user selects a bounding box on the map.
- The coordinates of the bounding box are sent to the server via the `/minmax` endpoint.

### 2. Generating a Shapefile
- The server processes the bounding box coordinates using `create_bbox_shapefile` from `create_shapefile.py`.
- A shapefile is created based on the selected area.

### 3. Downloading Satellite Imagery
- The server retrieves high-resolution satellite imagery for the bounding box using `download_satellite_imagery` from `download_imagery.py`.

### 4. Segmenting the Satellite Image
- The downloaded image is processed using `segment_satellite_image` from `segment_land_hqsam.py`.
- The segmentation results are saved as GeoJSON data.

### 5. Displaying Segmentation Results
- The client fetches the segmentation data from the server.
- The segmented land areas are displayed as polygons on the map.
- Users can interact with these polygons by selecting, editing, or deleting them.

## MapComponent Overview

The [`MapComponent`](client/src/components/shared/MapComponent.jsx) in the file [`client/src/components/shared/MapComponent.jsx`](client/src/components/shared/MapComponent.jsx) is a React component that integrates with the Leaflet library to create an interactive map. Here are the key details and functionalities of the component:

### Key Functionalities

#### 1. Map Initialization:
- The map is initialized using `MapContainer` from `react-leaflet`.
- The map is centered at a default position defined by `DEFAULT_POSITION` from the configuration file.

#### 2. Layers Control:
- The map includes two base layers: OpenStreetMap and Google Satellite.
- An overlay layer for segmentation data is also included.

#### 3. Drawing and Editing Features:
- The component uses `react-leaflet-draw` to allow users to draw and edit shapes on the map.
- The `EditControl` component handles the creation, editing, and deletion of shapes.
- When a shape is created or edited, a text input modal (`TextInput`) is displayed to allow users to add or edit text associated with the shape.

#### 4. Segmentation Data:
- The component fetches segmentation data from a server endpoint (`/get-segments`) and displays it as a GeoJSON layer on the map.
- Polygons in the segmentation data can be selected, deselected, and hovered over, with different styles applied based on their state.

#### 5. Selected Polygons Counter:
- A counter is displayed at the bottom right of the map, showing the number of selected polygons.

## AI Model Integration

- The component integrates with a segmentation model called **HQ-SAM** (High-Quality Segment Anything Model).
- The model is used to segment satellite images and generate masks and annotations.
- The model file (`sam_hq_vit_h.pth`) is downloaded from a specified URL if it does not already exist in the cache directory.

## Prerequisites

Before you begin, ensure you have the following installed:

- Node.js
- npm or yarn
- Python 3.9
- Conda

Additionally, set the following environment variable before running the application:

```bash
export QT_QPA_PLATFORM=offscreen
```

## Installation

### Clone the Repository

```bash
git clone https://github.com/crizmo/TerraBound.git
cd TerraBound
```

### Setting Up the Client

1. Navigate to the client directory:

   ```bash
   cd client
   ```

2. Install the dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```

4. Open your browser and navigate to http://localhost:3000.

### Setting Up the Server

1. Navigate to the server directory:

   ```bash
   cd server
   ```

2. Create a Conda environment:

   ```bash
   conda env create -f ../environment.yml
   ```

3. Activate the Conda environment:

   ```bash
   conda activate samgeo
   ```

4. Install additional Python dependencies:

   ```bash
   pip install -r ../requirements.txt
   ```

5. Start the Flask server:

   ```bash
   python server.py
   ```

6. The server will be running on http://127.0.0.1:5010.

## Usage

### Client

- **Creating Features**: Use the drawing tools on the map to create points, lines, and polygons.
- **Editing Features**: Click on a feature to edit its properties or delete it.
- **Text Mode**: Toggle the text mode to attach text to features.
- **Sidebar**: View and search for features in the sidebar.
- **Segmentation**: Use the segmentation functionality to process satellite images and visualize the results.

### Server

- **Endpoints**:
  - `/`: Basic endpoint to check if the server is running.
  - `/minmax`: Endpoint to receive bounding box coordinates and process satellite imagery.
