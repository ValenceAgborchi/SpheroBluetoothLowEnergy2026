from flask import Flask, jsonify, request
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


@app.route('/colour', methods=['POST'])
def set_led_color():
    data = request.get_json()
    controller.set_led_color(data['r'], data['g'], data['b'])
    return jsonify ({'success': True})




@app.route('/roll', methods=['POST'])
def roll():
    controller.roll(100, 0, 2)
    return jsonify({'success': True})

@app.route('/spin', methods=['POST'])
def spin():
    controller.spin(360, 2)
    return jsonify({'success': True})

@app.route('/stop', methods=['POST'])
def stop():
    controller.stop()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(port=5000)