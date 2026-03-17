import os
import random
try:
    import tensorflow as tf
except ImportError:
    tf = None
import sys
import pathlib
_BASE_DIR = pathlib.Path(__file__).parent.parent
sys.path.append(str(_BASE_DIR))
from preprocessing.image_processor import preprocess_for_cnn

def predict(image_path, model_path_or_instance='../models/document_cnn_v1.h5'):
    """
    Runs inference on a single image.
    If the model doesn't exist, it falls back to a mock prediction for development.
    
    Input:
        image_path: string path to image
        model_path_or_instance: string path to saved .h5 model, OR an already loaded tf.keras.Model instance
    
    Output:
    {
        "score": 0.85,           # 0.0 (fake) to 1.0 (real)
        "label": "real",         # "real" or "fake"
        "confidence": 0.85       # same as score for binary
    }
    """
    
    # 1. Provide mock return if model not trained yet
    if isinstance(model_path_or_instance, str) and not os.path.exists(model_path_or_instance):
        # Fall back to mock prediction based on Phase A strategy
        print(f"WARNING: Model not found at '{model_path_or_instance}'. Using mock prediction.")
        score = round(random.uniform(0.60, 0.95), 4)
        return {
            "score": score,
            "label": "real" if score >= 0.50 else "fake",
            "confidence": score if score >= 0.50 else float(1 - score),
            "is_mock": True
        }
    
    # 2. Real Prediction
    if tf is None:
        raise ImportError("Tensorflow is not installed, but a real model path was provided. Prediction impossible.")

    try:
        image = preprocess_for_cnn(image_path)
    except Exception as e:
        return {"error": f"Failed to preprocess image: {e}"}
        
    if isinstance(model_path_or_instance, str):
        model = tf.keras.models.load_model(model_path_or_instance)
    else:
        model = model_path_or_instance
        
    prediction = model.predict(image, verbose=0)[0][0]
    score = float(prediction)
    
    return {
        "score": score,
        "label": "real" if score >= 0.50 else "fake",
        "confidence": score if score >= 0.50 else float(1 - score),
        "is_mock": False
    }
