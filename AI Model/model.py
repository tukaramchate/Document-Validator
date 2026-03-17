import os
import logging
from cnn.predict import predict
from ocr.text_extractor import extract_text
from ocr.field_parser import parse_fields
from verification.db_matcher import match_against_db
from verification.score_calculator import calculate_final_score

logger = logging.getLogger(__name__)

class DocumentValidator:
    """
    Main entry point for the AI Document Validation Pipeline.
    Coordinates CNN (visual), OCR (text), and DB verification.
    """
    def __init__(self, model_path='models/document_cnn_v1.h5'):
        self.model_path = os.path.join(os.path.dirname(__file__), model_path)
        self.cnn_model = None
        
    def load_model(self):
        """Loads the CNN model from disk. If not found, predict() will use mock fallback."""
        if os.path.exists(self.model_path):
            import tensorflow as tf
            try:
                self.cnn_model = tf.keras.models.load_model(self.model_path)
                logger.info(f"Loaded CNN model from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load CNN model: {e}")
        else:
            logger.warning(f"CNN model not found at {self.model_path}. Inference will run in mock mode.")
            
    def validate(self, image_path, db_record_fields=None):
        """
        Full validation pipeline.
        
        Args:
            image_path (str): Path to the document image.
            db_record_fields (dict): Expected fields to match against (e.g. from backend DB).
            
        Returns:
            dict: Complete validation result with sub-scores.
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
            
        # Step 3: Database Cross-Verification
        db_result = match_against_db(extracted_fields, db_record_fields)
        
        # Step 4: Combine Scores
        final = calculate_final_score(
            cnn_score=cnn_result.get("score", 0.0),
            ocr_confidence=ocr_result.get("confidence", 0.0),
            db_match_score=db_result.get("score", 0.0)
        )
        
        return {
            "cnn_result": cnn_result,
            "ocr_result": {
                "fields": extracted_fields,
                "confidence": ocr_result["confidence"]
            },
            "db_result": db_result,
            "final": final
        }
    
    def train(self, data_dir='data/', epochs=50, batch_size=32):
        """Train the CNN on real/fake dataset"""
        from cnn.train import train_model
        train_model(
            data_dir=os.path.join(os.path.dirname(__file__), data_dir),
            output_model_path=self.model_path,
            epochs=epochs,
            batch_size=batch_size
        )
