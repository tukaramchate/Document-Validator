import os
import logging
from src.cnn.predict import predict
from src.ocr.text_extractor import extract_text
from src.ocr.field_parser import parse_fields

logger = logging.getLogger(__name__)

class DocumentValidator:
    """
    Main entry point for the AI Document Validation Pipeline.
    Coordinates CNN (visual) and OCR (text) inference only.
    """
    def __init__(self, model_path='../saved_models/document_cnn_v1.pth'):
        self.model_path = os.path.join(os.path.dirname(__file__), model_path)
        self.cnn_model = None
        
    def load_model(self):
        """Loads the CNN model from disk. If not found, predict() will use mock fallback."""
        if os.path.exists(self.model_path):
            try:
                import torch
                checkpoint = torch.load(self.model_path, map_location='cpu', weights_only=False)
                self.cnn_model = self.model_path  # predict.py will handle loading
                logger.info(f"CNN model found at {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load CNN model: {e}")
        else:
            logger.warning(f"CNN model not found at {self.model_path}. Inference will run in mock mode.")
            
    def validate(self, image_path):
        """
        Full AI inference pipeline.
        
        Args:
            image_path (str): Path to the document image.

        Returns:
            dict: AI outputs only (cnn_result + ocr_result).
        """
        # Step 1: CNN Visual Analysis
        model_instance = self.cnn_model if self.cnn_model else self.model_path
        cnn_result = predict(image_path, model_path_or_instance=model_instance)
        
        # Step 2: OCR Text Extraction
        ocr_result = extract_text(image_path)
        
        # If Gemini returned unstructured text, use fallback parser
        # Usually Gemini returns a clean dict, but we double-check required keys
        extracted_fields = ocr_result["fields"]
        if "error" in extracted_fields or not extracted_fields.get("name"):
            logger.info("Using fallback regex parser on OCR text")
            extracted_fields = parse_fields(ocr_result["raw_text"])
        
        return {
            "cnn_result": cnn_result,
            "ocr_result": {
                "fields": extracted_fields,
                "confidence": ocr_result["confidence"]
            }
        }
    
    def train(self, data_dir='data/', epochs=50, batch_size=32):
        """Train the CNN on real/fake dataset"""
        from src.cnn.train_pytorch import train_model
        train_model(
            data_dir=os.path.join(os.path.dirname(__file__), data_dir),
            output_path=self.model_path,
            epochs=epochs,
            batch_size=batch_size
        )
