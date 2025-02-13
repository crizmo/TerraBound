import os
import leafmap
from samgeo.hq_sam import SamGeo
import matplotlib.pyplot as plt
import rasterio
import cv2
import numpy as np
from tqdm import tqdm
import gdown
import geopandas as gpd
from rasterio import features
from shapely.geometry import shape, Polygon

def setup_model():
    """Setup HQ-SAM model"""
    cache_dir = os.path.expanduser("~/.cache/torch/hub/checkpoints")
    os.makedirs(cache_dir, exist_ok=True)
    
    pth_path = os.path.join(cache_dir, "sam_hq_vit_h.pth")
    
    if not os.path.exists(pth_path):
        print("Downloading HQ-SAM model file...")
        gdown.download(
            "https://huggingface.co/lkeab/hq-sam/resolve/main/sam_hq_vit_h.pth",
            pth_path,
            quiet=False
        )
    
    return os.path.exists(pth_path)

def plot_results(image_path, annotations_path, output_dir, filename):
    """Create visualization plot showing original, mask, and overlay"""
    
    # Read original image
    with rasterio.open(image_path) as src:
        image = src.read()
        image = ((image - image.min()) * (255 / (image.max() - image.min()))).astype(np.uint8)
        image = np.transpose(image, (1,2,0))
        if image.shape[2] == 4:
            image = image[:,:,:3]
    
    # Read annotations
    with rasterio.open(annotations_path) as src:
        annotations = src.read()
        annotations = np.transpose(annotations, (1,2,0))
        if annotations.shape[2] == 4:
            annotations = annotations[:,:,:3]
    
    # Create overlay
    overlay = cv2.addWeighted(image, 0.7, annotations, 0.3, 0)
    
    # Create visualization plot
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
    
    ax1.imshow(image)
    ax1.set_title('Original Image')
    ax1.axis('off')
    
    ax2.imshow(annotations)
    ax2.set_title('Segmentation') 
    ax2.axis('off')
    
    ax3.imshow(overlay)
    ax3.set_title('Overlay')
    ax3.axis('off')
    
    plt.tight_layout()
    viz_filename = f'visualization_{os.path.splitext(filename)[0]}.png'
    plt.savefig(os.path.join(output_dir, viz_filename))
    plt.close()

def masks_to_shapefile(mask_path, output_shp_path, threshold_percentile=5):
    """
    Convert mask TIFF to shapefile with each segment as a polygon.
    Filters out smaller segments based on mask values.
    
    Args:
        mask_path: Path to the mask TIFF file
        output_shp_path: Path to save the output shapefile
        threshold_percentile: Percentile threshold (0-100) below which masks will be filtered out
    """
    # Read the mask raster
    with rasterio.open(mask_path) as src:
        mask = src.read(1)  # Read first band
        transform = src.transform
        crs = src.crs
    
    # Get unique values and calculate threshold
    unique_values = np.unique(mask[mask > 0])  # Exclude 0 which is background
    if len(unique_values) == 0:
        print(f"No valid masks found in {mask_path}")
        return
        
    threshold_value = np.percentile(unique_values, threshold_percentile)
    print(f"Filtering out masks with values below {threshold_value}")
    
    # Create filtered mask
    filtered_mask = mask.copy()
    filtered_mask[filtered_mask < threshold_value] = 0
    
    # Get shapes from filtered mask
    shapes = list(features.shapes(filtered_mask.astype(np.int32), filtered_mask > 0, transform=transform))
    
    if not shapes:
        print(f"No shapes remain after filtering for {mask_path}")
        return
    
    # Convert shapes to GeoDataFrame
    geometries = [shape(geom) for geom, val in shapes]
    values = [val for geom, val in shapes]
    
    gdf = gpd.GeoDataFrame({
        'geometry': geometries,
        'segment_id': values,
        'area': [geom.area for geom in geometries]  # Add area for reference
    }, crs=crs)
    
    # Sort by segment_id for better organization
    gdf = gdf.sort_values('segment_id', ascending=False)
    
    # Save to shapefile
    gdf.to_file(output_shp_path)
    print(f"Saved {len(gdf)} polygons to {output_shp_path}")

def segment_satellite_image():
    """Segment the temporary satellite image"""
    
    # Get the absolute path to TeraBound directory
    terabound_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Setup paths using absolute paths
    input_image = os.path.join(terabound_dir, "temp", "imagery", "temp_satellite.tif")
    output_dir = os.path.join(terabound_dir, "temp", "segmentation")
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if input exists
    if not os.path.exists(input_image):
        print(f"Error: Satellite image not found at {input_image}")
        return False
        
    # Setup model
    if not setup_model():
        print("Error: Failed to setup HQ-SAM model")
        return False
    
    try:
        print("\nStarting segmentation process...")
        print(f"Input image: {input_image}")
        
        # Modified sam_kwargs for agricultural plot detection
        sam_kwargs = {
            "points_per_side": 24,
            "pred_iou_thresh": 0.90,
            "stability_score_thresh": 0.95,
            "crop_n_layers": 0,
            "min_mask_region_area": 5000,
            "box_nms_thresh": 0.7,
            "crop_nms_thresh": 0.7,
            "crop_overlap_ratio": 0.34,
            "output_mode": "binary_mask"
        }
        
        sam = SamGeo(
            model_type="vit_h",
            sam_kwargs=sam_kwargs,
        )
        
        # Output paths
        masks_path = os.path.join(output_dir, "temp_masks.tif")
        annotations_path = os.path.join(output_dir, "temp_annotations.tif")
        shapefile_path = os.path.join(output_dir, "temp_polygons.shp")
        
        # Generate masks
        print("Generating segmentation masks...")
        sam.generate(input_image, output=masks_path, foreground=True, unique=True)
        
        # Generate colored annotations
        print("Creating annotations...")
        sam.show_anns(axis="off", alpha=1, output=annotations_path)
        
        # Convert masks to shapefile using the original function
        print("Converting to shapefile...")
        masks_to_shapefile(masks_path, shapefile_path)
        
        print("\nSegmentation complete!")
        print(f"✓ Masks saved: {masks_path}")
        print(f"✓ Annotations saved: {annotations_path}")
        print(f"✓ Shapefile saved: {shapefile_path}")
        
        return True
        
    except Exception as e:
        print(f"Error during segmentation: {str(e)}")
        return False

if __name__ == "__main__":
    segment_satellite_image() 