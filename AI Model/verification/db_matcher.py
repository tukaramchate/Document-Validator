from difflib import SequenceMatcher

def fuzzy_match(str1, str2, threshold=0.85):
    """
    Returns True if similarity >= threshold
    "Rahul Sharrna" vs "Rahul Sharma" -> similarity = 0.92 -> match = True
    "8.5" vs "7.2" -> similarity = 0.0 -> match = False
    """
    if not str1 or not str2:
        return {"match": False, "similarity": 0.0}
        
    similarity = SequenceMatcher(None, str(str1).lower(), str(str2).lower()).ratio()
    return {
        "match": similarity >= threshold,
        "similarity": round(similarity, 2)
    }

def match_against_db(extracted_fields, db_record_fields=None):
    """
    Compares extracted fields against a provided database record dict.
    Returns match score and individual field matches.
    """
    if not db_record_fields or not extracted_fields:
        return {
            "score": 0.0,
            "total_fields": 0,
            "matched_fields": 0,
            "details": {}
        }
        
    details = {}
    matched_count = 0
    total_checked = 0
    
    # We only score fields that exist in the DB record
    for key, db_value in db_record_fields.items():
        if key not in extracted_fields:
            continue
            
        total_checked += 1
        extracted_value = extracted_fields.get(key)
        
        # Exact match for numbers/IDs, fuzzy match for names/text
        is_string_field = isinstance(db_value, str) and not db_value.replace('.','',1).isdigit()
        
        if is_string_field:
            match_result = fuzzy_match(extracted_value, db_value)
        else:
            # Exact match for numbers with whitespace stripped
            clean_extracted = str(extracted_value).strip().lower() if extracted_value else ""
            clean_db = str(db_value).strip().lower() if db_value else ""
            is_match = clean_extracted == clean_db and bool(clean_db)
            match_result = {"match": is_match, "similarity": 1.0 if is_match else 0.0}
            
        details[key] = {
            "extracted": extracted_value,
            "db_value": db_value,
            "match": match_result["match"],
            "similarity": match_result["similarity"]
        }
        
        if match_result["match"]:
            matched_count += 1
            
    score = matched_count / total_checked if total_checked > 0 else 0.0
    
    return {
        "score": round(score, 4),
        "total_fields": total_checked,
        "matched_fields": matched_count,
        "details": details
    }
