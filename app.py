from flask import Flask, jsonify
from flask_cors import CORS
from sphero_controller import SpheroController


app = Flask(__name__)
CORS(app)
controller = SpheroController(mock_mode=False)


@app.route('/connect', methods=['POST'])
def connect():
    success = controller.connect()
    return jsonify ({'success' : success})


@app.route('/disconnect', methods=['POST'])
def disconnect():
    controller.disconnect()
    return jsonify({'success': True})




