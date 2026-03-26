import re

def parse_fields(raw_text):
    """
    Fallback parser that extracts structured fields from raw text using regex.
    This is used if the primary Gemini JSON extraction fails or returns unstructured text.
    """
    
    # Initialize empty fields matching our schema
    fields = {
        "name": None,
        "id_number": None,
        "course": None,
        "branch": None,
        "year": None,
        "cgpa": None,
        "sgpa": None,
        "certificate_id": None,
        "institution": None,
        "date": None
    }
    
    if not raw_text or not isinstance(raw_text, str):
        return fields
        
    line_patterns = {
        "name": [r"(?:Name|Student Name|Candidate Name)\s*[:\-]\s*(.+)"],
        "id_number": [r"(?:Roll No|Roll Number|Reg No|Registration No|ID Number)\s*[:\-]\s*([\w\/\-]+)"],
        "course": [r"(?:Course|Program|Degree)\s*[:\-]\s*(.+)"],
        "branch": [r"(?:Branch|Specialization|Discipline)\s*[:\-]\s*(.+)"],
        "cgpa": [r"(?:CGPA|GPA|Cumulative Grade)\s*[:\-]\s*([\d\.]+)"],
        "sgpa": [r"(?:SGPA|Semester Grade)\s*[:\-]\s*([\d\.]+)"],
        "date": [r"(?:Date|Issued on|Date of Issue)\s*[:\-]\s*([\d\/\-\.]+)"],
        "certificate_id": [r"(?:Certificate ID|Certificate No|Ref No)\s*[:\-]\s*([\w\/\-]+)"],
        "institution": [r"(?:Institution|University|College|Institute)\s*[:\-]\s*(.+)"],
    }
    
    # Line by line extraction
    lines = raw_text.split('\n')
    for line in lines:
        for field, patterns in line_patterns.items():
            if fields[field]: # Skip if already found
                continue
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    fields[field] = match.group(1).strip()
                    break
                    
    # Broad institution match
    inst_match = re.search(r"([\w\s]+ (?:University|Institute of Technology|College))", raw_text, re.IGNORECASE)
    if inst_match:
        fields["institution"] = inst_match.group(1).strip()
        
    return fields
