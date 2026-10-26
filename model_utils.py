"""Model inference, image validation, and preprocessing pipeline.

Provides robust image sanitization, corrupt file detection, CNN inference,
and confidence/uncertainty evaluation.
"""

from typing import Dict, Any, Tuple, Optional, List
import io
import json
import os
import numpy as np
from PIL import Image

from traffic_sign_meta import get_sign_info, TRAFFIC_SIGN_METADATA

# Default image preprocessing specifications
DEFAULT_IMAGE_SIZE = (48, 48)  # Height, Width
CONFIDENCE_THRESHOLD = 0.80     # Minimum confidence to consider recognition reliable
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".ppm"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


class ImageValidationError(Exception):
    """Raised when an uploaded image fails validation."""
    pass


class ModelUnavailableError(Exception):
    """Raised when recognition is requested but no model is loaded."""
    pass


def validate_image_file(file_bytes: bytes, filename: str) -> Image.Image:
    """Validate file bytes, extension, corruption, and visual suitability.

    Returns:
        PIL Image in RGB format if valid.

    Raises:
        ImageValidationError: If the file is invalid, corrupt, or empty.
    """
    if not file_bytes or len(file_bytes) == 0:
        raise ImageValidationError("Uploaded file is empty (0 bytes). Please select a valid image.")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES / (1024 * 1024)
        raise ImageValidationError(f"File size exceeds the {max_mb:.0f} MB limit.")

    # Extension check
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ImageValidationError(
            f"Unsupported file format '{ext}'. Allowed formats are: {allowed}."
        )

    # Decompression & corruption check using Pillow
    try:
        # Wrap bytes in BytesIO
        stream = io.BytesIO(file_bytes)
        img = Image.open(stream)
        # Verify integrity of file headers and structure
        img.verify()

        # Reopen after verify (verify closes stream in Pillow)
        stream.seek(0)
        img = Image.open(stream)
        # Convert to standard RGB (handles CMYK, grayscale, RGBA)
        img_rgb = img.convert("RGB")
    except Exception as e:
        raise ImageValidationError(
            f"Image file is corrupt, truncated, or cannot be decoded: {str(e)}"
        )

    width, height = img_rgb.size
    if width < 8 or height < 8:
        raise ImageValidationError(
            f"Image dimensions ({width}x{height}) are too small for traffic sign analysis (minimum 8x8)."
        )

    # Visual suitability check: detect uniform / blank / solid color images
    np_img = np.array(img_rgb, dtype=np.float32)
    std_dev = float(np.std(np_img))
    if std_dev < 3.0:
        raise ImageValidationError(
            "The image appears to be a solid blank color with no discernible features. Please provide an image of a traffic sign."
        )

    return img_rgb


def preprocess_image(img: Image.Image, target_size: Tuple[int, int] = DEFAULT_IMAGE_SIZE) -> np.ndarray:
    """Preprocess PIL Image for CNN input.

    - Resizes to target dimension (e.g. 48x48) using high-quality Lanczos resampling.
    - Converts to float32.
    - Normalizes pixel intensity to [0.0, 1.0].
    - Adds batch dimension: (1, height, width, channels).
    """
    resized = img.resize(target_size, Image.Resampling.LANCZOS)
    arr = np.array(resized, dtype=np.float32)

    # Normalize to [0.0, 1.0]
    arr_normalized = arr / 255.0

    # Expand dims for batch: (1, H, W, C)
    batch_tensor = np.expand_dims(arr_normalized, axis=0)
    return batch_tensor


class TrafficSignClassifier:
    """Manages model loading, health checking, and inference."""

    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.model = None
        self.model_path: Optional[str] = None
        self.model_loaded = False
        self.target_size = DEFAULT_IMAGE_SIZE
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        self.class_indices: Optional[Dict[str, int]] = None
        self.load_error: Optional[str] = None

        self._attempt_load()

    def _attempt_load(self):
        """Attempt to locate and load a trained Keras/TensorFlow model."""
        if not os.path.exists(self.models_dir):
            self.model_loaded = False
            self.load_error = f"Models directory '{self.models_dir}' does not exist."
            return

        # Check for preprocessing configuration
        config_path = os.path.join(self.models_dir, "preprocessing_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if "image_size" in config and len(config["image_size"]) == 2:
                        self.target_size = tuple(config["image_size"])
                    if "confidence_threshold" in config:
                        self.confidence_threshold = float(config["confidence_threshold"])
            except Exception as e:
                print(f"[WARN] Could not parse preprocessing_config.json: {e}")

        # Check for class indices
        indices_path = os.path.join(self.models_dir, "class_indices.json")
        if os.path.exists(indices_path):
            try:
                with open(indices_path, "r", encoding="utf-8") as f:
                    self.class_indices = json.load(f)
            except Exception as e:
                print(f"[WARN] Could not parse class_indices.json: {e}")

        # Find candidate model files (.keras, .h5)
        candidates = [
            os.path.join(self.models_dir, "traffic_sign_cnn.keras"),
            os.path.join(self.models_dir, "traffic_sign_cnn.h5"),
        ]

        # Also search for any other .keras or .h5 in models_dir
        for fname in os.listdir(self.models_dir):
            if (fname.endswith(".keras") or fname.endswith(".h5")) and fname not in [
                "traffic_sign_cnn.keras",
                "traffic_sign_cnn.h5",
            ]:
                candidates.append(os.path.join(self.models_dir, fname))

        chosen_path = None
        for cand in candidates:
            if os.path.exists(cand):
                chosen_path = cand
                break

        if not chosen_path:
            self.model_loaded = False
            self.load_error = (
                "No trained model file (.keras or .h5) found in models/ folder."
            )
            return

        # Attempt to load with Keras
        try:
            import tensorflow as tf
            # Suppress verbose TensorFlow logging
            os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
            self.model = tf.keras.models.load_model(chosen_path)
            self.model_path = chosen_path
            self.model_loaded = True
            self.load_error = None
            print(f"[INFO] Successfully loaded model from '{chosen_path}'")
        except Exception as e:
            self.model = None
            self.model_loaded = False
            self.load_error = f"Failed to load model from '{chosen_path}': {str(e)}"
            print(f"[ERROR] {self.load_error}")

    def reload(self):
        """Force reloading the model (e.g., after training finishes)."""
        self._attempt_load()

    def get_status(self) -> Dict[str, Any]:
        """Return operational health status."""
        return {
            "model_available": self.model_loaded,
            "model_path": self.model_path,
            "target_image_size": list(self.target_size),
            "confidence_threshold": self.confidence_threshold,
            "total_supported_classes": len(TRAFFIC_SIGN_METADATA),
            "error_detail": self.load_error,
        }

    def predict(self, img: Image.Image) -> Dict[str, Any]:
        """Perform CNN prediction on an image.

        Raises:
            ModelUnavailableError: If no model is loaded.
        """
        if not self.model_loaded or self.model is None:
            raise ModelUnavailableError(
                "Traffic sign recognition is not available yet because a compatible trained model has not been installed. "
                "Please add a trained model and try again."
            )

        # Preprocess using consistent target size and normalization
        tensor = preprocess_image(img, target_size=self.target_size)

        # Run inference
        raw_preds = self.model.predict(tensor, verbose=0)[0]

        # Top prediction
        predicted_idx = int(np.argmax(raw_preds))
        confidence = float(raw_preds[predicted_idx])

        # Get sorted predictions for top candidates
        sorted_indices = np.argsort(raw_preds)[::-1]
        top_candidates: List[Dict[str, Any]] = []
        for rank, idx in enumerate(sorted_indices[:3]):
            info = get_sign_info(int(idx))
            top_candidates.append({
                "rank": rank + 1,
                "class_id": int(idx),
                "name": info["name"],
                "confidence_pct": round(float(raw_preds[idx]) * 100, 2),
            })

        # Margin between top 1 and top 2 predictions
        second_confidence = float(raw_preds[sorted_indices[1]]) if len(sorted_indices) > 1 else 0.0
        margin = confidence - second_confidence

        # A sign is considered reliably detected only if:
        # 1. Top confidence meets or exceeds confidence threshold (>= 80%)
        # 2. Significant margin over alternative candidate (>= 35%)
        sign_detected = (confidence >= self.confidence_threshold) and (margin >= 0.35)
        is_uncertain = not sign_detected

        # Retrieve comprehensive sign metadata
        sign_info = get_sign_info(predicted_idx)
        pct = round(confidence * 100, 1)
        thresh_pct = round(self.confidence_threshold * 100, 0)

        if sign_detected:
            display_title = sign_info["name"]
            display_category = sign_info["category"]
            uncertainty_message = None
            action_text = sign_info["action"]
            description_text = sign_info["description"]
        else:
            display_title = "No Recognizable Traffic Sign Detected"
            display_category = "Ambiguous / Non-Sign Scene"
            uncertainty_message = (
                f"The image does not match any recognized traffic sign with high confidence ({pct}% vs {thresh_pct}% threshold). "
                "The model detected features of a natural landscape, road scene, or non-sign object rather than a clear traffic sign."
            )
            action_text = "No traffic sign regulation identified. Exercise normal roadway awareness."
            description_text = (
                f"No verified traffic sign detected. The closest ambiguous visual match was '{sign_info['name']}' ({pct}%), "
                "which falls below the required threshold for safe traffic sign recognition."
            )

        return {
            "success": True,
            "sign_detected": sign_detected,
            "display_title": display_title,
            "display_category": display_category,
            "class_id": predicted_idx,
            "name": sign_info["name"],
            "category": sign_info["category"],
            "shape": sign_info["shape"],
            "description": description_text,
            "action": action_text,
            "confidence": round(confidence, 4),
            "confidence_pct": round(confidence * 100, 2),
            "margin": round(margin, 4),
            "is_uncertain": is_uncertain,
            "uncertainty_message": uncertainty_message,
            "top_candidates": top_candidates,
            "limitation_notice": (
                "Note: Standard closed-set CNN classifiers distribute probability across their 43 known classes. "
                "A low-confidence or high-entropy warning indicates uncertainty, but a dedicated open-set detector is recommended to definitively reject arbitrary non-traffic images."
            ),
        }
