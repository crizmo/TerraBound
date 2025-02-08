from flask import Flask, request, jsonify # type: ignore
from flask_cors import CORS  # type: ignore
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def index():
    return 'Hello World'

@app.route('/minmax', methods=['POST'])
def minmax():
    data = request.get_json()
    min_value = data.get('min')
    max_value = data.get('max')
    print(f'Received Min: {min_value}, Max: {max_value}')
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(debug=True)