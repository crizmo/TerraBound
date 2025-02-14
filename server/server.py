from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import sys
import geopandas as gpd

# Add parent directory to path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from create_shapefile import create_bbox_shapefile
from download_imagery import download_satellite_imagery
from segment_land_hqsam import segment_satellite_image
from qgis.core import QgsApplication

app = Flask(__name__)
CORS(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Initialize QGIS Application
qgs = QgsApplication([], False)
qgs.initQgis()

@app.route('/')
def index():
    return 'Hello World'

@app.route('/minmax', methods=['POST'])
def minmax():
    try:
        data = request.get_json()
        min_coords = data.get('min')  # [lat, lon]
        max_coords = data.get('max')  # [lat, lon]
        
        print(f'Received Min: {min_coords}, Max: {max_coords}')
        
        # Reformat coordinates for shapefile creation [min_lon, min_lat, max_lon, max_lat]
        bbox_coords = [min_coords[1], min_coords[0], max_coords[1], max_coords[0]]
        
        # Create temporary shapefile
        temp_shapefile = create_bbox_shapefile(bbox_coords, "temp_region")
        
        # Create output directory for imagery
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp', 'imagery')
        os.makedirs(output_dir, exist_ok=True)
        
        # Download imagery using the temporary shapefile
        output_image = os.path.join(output_dir, 'temp_satellite.tif')
        result = download_satellite_imagery(qgs, temp_shapefile, output_image)
        
        if result['success']:
            print("\nComplete workflow status:")
            print("✓ Shapefile created")
            print("✓ Satellite imagery downloaded")
            print("✓ Starting segmentation...")
            
            # Perform segmentation
            seg_result = segment_satellite_image()
            
            if seg_result:
                print("✓ Segmentation completed successfully")
                return jsonify({
                    'status': 'success',
                    'shapefile': temp_shapefile,
                    'imagery': output_image,
                    'message': 'Workflow completed successfully'
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Segmentation failed'
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'message': result['error']
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/get-segments', methods=['GET'])
def get_segments():
    try:
        shapefile_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'temp', 'segmentation', 'temp_polygons.shp')
        
        if not os.path.exists(shapefile_path):
            return jsonify({
                'status': 'error',
                'message': 'Segmentation shapefile not found'
            }), 404
            
        # Read shapefile and convert to GeoJSON
        gdf = gpd.read_file(shapefile_path)
        geojson_data = gdf.to_crs(epsg=4326).to_json()  # Convert to WGS84 for web mapping
        
        return jsonify({
            'status': 'success',
            'data': geojson_data
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5010
    print(f'Server running on http://{host}:{port}')
    app.run(debug=True, host=host, port=port)