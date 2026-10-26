"""Flask backend for Intelligent Traffic Sign Recognition Web Application.

Provides endpoints for UI serving, operational health checking, and CNN inference.
"""

import base64
import os
import sys
import traceback
from flask import Flask, render_template, request, jsonify

from model_utils import (
    TrafficSignClassifier,
    validate_image_file,
    ImageValidationError,
    ModelUnavailableError,
)
from traffic_sign_meta import TRAFFIC_SIGN_METADATA

app = Flask(__name__)
# Limit upload payload to 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# Instantiate classifier once at startup
classifier = TrafficSignClassifier(models_dir=os.path.join(os.path.dirname(__file__), "models"))


@app.route("/")
def index():
    """Render the main single-page web interface."""
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    """Report application health and model readiness status."""
    return jsonify({
        "status": "healthy",
        "flask_running": True,
        "model_status": classifier.get_status(),
    }), 200


@app.route("/api/classes", methods=["GET"])
def list_classes():
    """Return all 43 traffic sign classes and their descriptions for reference."""
    classes = [
        {
            "id": item["id"],
            "code": item["code"],
            "name": item["name"],
            "category": item["category"],
            "shape": item["shape"],
            "description": item["description"],
            "action": item["action"],
        }
        for item in TRAFFIC_SIGN_METADATA.values()
    ]
    return jsonify({"total": len(classes), "classes": classes}), 200


@app.route("/predict", methods=["POST"])
def predict():
    """Accept an uploaded image, validate it, and perform CNN prediction.

    Accepts:
        - multipart/form-data with file field 'image' (or 'file')
        - application/json with base64 data URL under 'image'
    """
    file_bytes = None
    filename = "upload.png"

    # 1. Parse image from request
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        image_data = payload.get("image", "")
        if not image_data:
            return jsonify({
                "success": False,
                "error": "No image data found in request payload.",
            }), 400

        # Decode base64 data URL
        try:
            if "," in image_data:
                header, encoded = image_data.split(",", 1)
                # Infer extension from header e.g. data:image/png;base64
                if "jpeg" in header or "jpg" in header:
                    filename = "captured.jpg"
                elif "png" in header:
                    filename = "captured.png"
                elif "webp" in header:
                    filename = "captured.webp"
                else:
                    filename = "captured.png"
            else:
                encoded = image_data
            file_bytes = base64.b64decode(encoded)
        except Exception:
            return jsonify({
                "success": False,
                "error": "Failed to decode base64 image data.",
            }), 400

    elif "image" in request.files or "file" in request.files:
        file_obj = request.files.get("image") or request.files.get("file")
        if not file_obj or file_obj.filename == "":
            return jsonify({
                "success": False,
                "error": "No file was selected for upload.",
            }), 400
        filename = file_obj.filename or "upload.png"
        try:
            file_bytes = file_obj.read()
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Failed to read uploaded file: {str(e)}",
            }), 400
    else:
        return jsonify({
            "success": False,
            "error": "Invalid request: Please submit an image via multipart form-data or JSON base64.",
        }), 400

    # 2. Validate image
    try:
        pil_image = validate_image_file(file_bytes, filename)
    except ImageValidationError as ive:
        return jsonify({
            "success": False,
            "error": str(ive),
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Image validation error: {str(e)}",
        }), 400

    # 3. Model availability check & prediction
    try:
        prediction_result = classifier.predict(pil_image)
        return jsonify(prediction_result), 200

    except ModelUnavailableError as mue:
        # 503 Service Unavailable when model is not installed yet
        return jsonify({
            "success": False,
            "model_available": False,
            "error": str(mue),
        }), 503

    except Exception as e:
        # Do not expose internal stack trace to client
        sys.stderr.write(f"[ERROR in /predict]: {str(e)}\n")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "An unexpected server error occurred during prediction. Please try another image.",
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n==================================================")
    print(f" Intelligent Traffic Sign Recognition System")
    print(f" Server starting on http://127.0.0.1:{port}")
    print(f" Model loaded: {classifier.model_loaded}")
    if not classifier.model_loaded:
        print(f" Note: {classifier.load_error}")
    print(f"==================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
