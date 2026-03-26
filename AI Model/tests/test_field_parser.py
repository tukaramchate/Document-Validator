"""
Unit tests for the regex fallback field parser (src/ocr/field_parser.py).
Run with: pytest tests/test_field_parser.py -v
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.ocr.field_parser import parse_fields


SAMPLE_CERTIFICATE_TEXT = """
UNIVERSITY OF TECHNOLOGY
Certificate of Achievement

Student Name: Rahul Sharma
Roll Number: CS2021001
Course: Bachelor of Technology
Branch: Computer Science and Engineering
Institution: University of Technology
CGPA: 8.75
SGPA: 9.10
Date: 15/06/2024
Certificate No: CERT-2024-00123
"""

SAMPLE_MARKSHEET_TEXT = """
Karnataka State University
Reg No: KSU/2020/12345
Degree: Master of Science
Specialization: Data Science
Cumulative Grade: 9.0
Semester Grade: 8.5
Issued on: 01-07-2024
"""


class TestParseFieldsBasic:
    def test_returns_dict_with_all_keys(self):
        result = parse_fields(SAMPLE_CERTIFICATE_TEXT)
        expected_keys = {"name", "id_number", "course", "branch", "year", "cgpa", "sgpa",
                         "certificate_id", "institution", "date"}
        assert set(result.keys()) == expected_keys

    def test_extracts_name(self):
        result = parse_fields(SAMPLE_CERTIFICATE_TEXT)
        assert result["name"] == "Rahul Sharma"

    def test_extracts_id_number(self):
        result = parse_fields(SAMPLE_CERTIFICATE_TEXT)
        assert result["id_number"] == "CS2021001"

    def test_extracts_course(self):
        result = parse_fields(SAMPLE_CERTIFICATE_TEXT)
        assert result["course"] is not None
        assert "Technology" in result["course"]

    def test_extracts_branch(self):
        result = parse_fields(SAMPLE_CERTIFICATE_TEXT)
        assert result["branch"] is not None
        assert "Computer Science" in result["branch"]

    def test_extracts_cgpa(self):
        result = parse_fields(SAMPLE_CERTIFICATE_TEXT)
        assert result["cgpa"] == "8.75"

    def test_extracts_sgpa(self):
        result = parse_fields(SAMPLE_CERTIFICATE_TEXT)
        assert result["sgpa"] == "9.10"

    def test_extracts_date(self):
        result = parse_fields(SAMPLE_CERTIFICATE_TEXT)
        assert result["date"] == "15/06/2024"

    def test_extracts_certificate_id(self):
        result = parse_fields(SAMPLE_CERTIFICATE_TEXT)
        assert result["certificate_id"] is not None

    def test_extracts_institution(self):
        result = parse_fields(SAMPLE_CERTIFICATE_TEXT)
        assert result["institution"] is not None
        assert "Technology" in result["institution"]


class TestParseFieldsAlternativeKeywords:
    def test_reg_no_variant(self):
        result = parse_fields(SAMPLE_MARKSHEET_TEXT)
        assert result["id_number"] == "KSU/2020/12345"

    def test_specialization_as_branch(self):
        result = parse_fields(SAMPLE_MARKSHEET_TEXT)
        assert result["branch"] is not None
        assert "Data Science" in result["branch"]

    def test_degree_as_course(self):
        result = parse_fields(SAMPLE_MARKSHEET_TEXT)
        assert result["course"] is not None


class TestParseFieldsEdgeCases:
    def test_empty_string_returns_all_nulls(self):
        result = parse_fields("")
        for val in result.values():
            assert val is None

    def test_none_input_returns_all_nulls(self):
        result = parse_fields(None)
        for val in result.values():
            assert val is None

    def test_irrelevant_text_returns_mostly_nulls(self):
        result = parse_fields("This is a random document with no academic information.")
        # Most fields should be None for unrelated text
        none_count = sum(1 for v in result.values() if v is None)
        assert none_count >= 8
