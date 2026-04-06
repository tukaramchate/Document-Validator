"""
Shared test fixtures for the AI Model test suite.

Provides reusable fixtures for:
  - FastAPI TestClient with mocked services.
  - Fake image generation.
  - Pipeline component instances.

Usage:
    pytest tests/ -v
"""
import os
import sys

import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set test environment BEFORE importing anything from the app
os.environ["APP_ENV"] = "testing"
os.environ["GEMINI_API_KEY"] = "test-key-mock"


@pytest.fixture(scope="session")
def fake_image_bytes():
    """Generate a minimal JPEG image for testing."""
    from PIL import Image
    import io

    img = Image.new("RGB", (200, 300), color="white")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture(scope="session")
def fake_image_pil():
    """Generate a PIL Image for testing."""
    from PIL import Image

    return Image.new("RGB", (200, 300), color="white")


@pytest.fixture(scope="session")
def sample_extracted_text():
    """Sample OCR text mimicking a real marksheet."""
    return """
    INDIAN INSTITUTE OF TECHNOLOGY BOMBAY
    Statement of Marks
    Semester Examination - December 2023

    Name: Rahul Sharma
    Roll No: 2019BCS0045
    Course: B.Tech
    Branch: Computer Science and Engineering
    Semester: 7

    Subject Code  Subject Name            Credits  Grade  Grade Point
    CS301         Data Structures         4        A+     10.0
    CS302         Operating Systems       4        A      9.0
    CS303         Database Systems        3        B+     8.0
    MA201         Linear Algebra          3        A      9.0
    HS301         English Communication   2        A+     10.0

    SGPA: 9.25
    CGPA: 8.75
    Result: Pass

    Date of Issue: 15/05/2024
    Certificate No: IIT-B/2024/SEM7/045
    """


@pytest.fixture(scope="session")
def sample_extracted_fields():
    """Sample structured fields in the new nested schema."""
    return {
        "student_info": {
            "name": "Rahul Sharma",
            "roll_number": "2019BCS0045",
            "enrollment_number": None,
            "father_name": None,
            "mother_name": None,
            "date_of_birth": None,
            "course": "B.Tech",
            "branch": "Computer Science and Engineering",
            "semester": "7",
            "year_of_study": None,
            "academic_year": "2023-24",
        },
        "institution_info": {
            "name": "Indian Institute of Technology Bombay",
            "abbreviation": "IITB",
            "city": "Mumbai",
            "state": "Maharashtra",
        },
        "grades": [
            {
                "subject_code": "CS301",
                "subject_name": "Data Structures",
                "credits": 4,
                "marks_obtained": None,
                "max_marks": None,
                "grade": "A+",
                "grade_point": 10.0,
            },
        ],
        "results": {
            "sgpa": 9.25,
            "cgpa": 8.75,
            "percentage": None,
            "total_marks_obtained": None,
            "total_max_marks": None,
            "result_status": "Pass",
            "division": None,
        },
        "verification_info": {
            "issue_date": "15/05/2024",
            "certificate_number": "IIT-B/2024/SEM7/045",
            "qr_code_data": None,
            "examination_month_year": "December 2023",
        },
    }
