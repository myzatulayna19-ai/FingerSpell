import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from gesture_engine import recognize_gesture

# Ensure Flask locates figma/dist static files
app = Flask(__name__, static_folder="figma/dist", static_url_path="")
CORS(app)


def decode_image(base64_string):
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    image_bytes = base64.b64decode(base64_string)
    np_array = np.frombuffer(image_bytes, np.uint8)
    return cv2.imdecode(np_array, cv2.IMREAD_COLOR)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        image_data = data.get("image")
        target_gesture = data.get("target") or "A"

        if not image_data:
            return jsonify({"error": "No image data provided"}), 400

        frame = decode_image(image_data)
        result = recognize_gesture(frame, target_gesture=target_gesture)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)