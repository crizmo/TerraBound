import geopandas as gpd
from shapely.geometry import box
import os

def create_bbox_shapefile(coordinates, region_name):
    """
    Create a shapefile from bounding box coordinates.
    
    Args:
        coordinates (list): [min_lon, min_lat, max_lon, max_lat] in EPSG:4326
        region_name (str): Name of the region
    
    Returns:
        str: Path to the created shapefile
    """
    try:
        # Create Shapely box from coordinates
        min_lon, min_lat, max_lon, max_lat = coordinates
        bbox = box(min_lon, min_lat, max_lon, max_lat)
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(
            {
                'reg_name': [region_name],
                'geometry': [bbox]
            },
            crs='EPSG:4326'  # Input coordinates are in WGS84
        )
        
        # Convert to Web Mercator for satellite imagery
        gdf = gdf.to_crs('EPSG:3857')
        
        # Create temp directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(__file__), 'temp', 'shapefiles')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save shapefile
        output_path = os.path.join(output_dir, f'{region_name}.shp')
        gdf.to_file(output_path)
        
        print(f"Created shapefile at: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error creating shapefile: {str(e)}")
        raise 