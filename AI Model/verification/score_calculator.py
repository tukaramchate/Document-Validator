def calculate_final_score(cnn_score, ocr_confidence, db_match_score):
    """
    Weighted scoring formula:
        CNN Visual Analysis:         40% weight
        OCR Extraction Confidence:   20% weight
        Database Match Score:        40% weight
    """
    
    WEIGHTS = {"cnn": 0.4, "ocr": 0.2, "db": 0.4}
    
    # Ensure inputs are floats
    cnn_score = float(cnn_score)
    ocr_confidence = float(ocr_confidence)
    db_match_score = float(db_match_score)
    
    final_score = (
        (cnn_score * WEIGHTS["cnn"]) +
        (ocr_confidence * WEIGHTS["ocr"]) +
        (db_match_score * WEIGHTS["db"])
    )
    
    if final_score >= 0.90:
        verdict = "AUTHENTIC"
    elif final_score >= 0.70:
        verdict = "SUSPICIOUS"
    else:
        verdict = "FAKE"
    
    return {
        "final_score": round(final_score, 4),
        "verdict": verdict,
        "breakdown": {
            "cnn_contribution": round(cnn_score * WEIGHTS["cnn"], 4),
            "ocr_contribution": round(ocr_confidence * WEIGHTS["ocr"], 4),
            "db_contribution": round(db_match_score * WEIGHTS["db"], 4)
        }
    }
