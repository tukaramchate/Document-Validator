"""
End-to-end integration test script for the AI Model pipeline.
Run: python scripts/integration_test.py
"""
import json
import os
import sys
import warnings
warnings.filterwarnings("ignore")

# Load .env for GEMINI_API_KEY
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
except ImportError:
    pass

from src.pipeline import DocumentValidator
from src.interfaces import PipelineResult, ExtractionResult

PASS = "[PASS]"
FAIL = "[FAIL]"
SKIP = "[SKIP]"

def check(condition: bool, msg: str) -> bool:
    status = PASS if condition else FAIL
    print(f"  {status}: {msg}")
    return condition

# --- Initialise pipeline -------------------------------------
print("Loading DocumentValidator...")
validator = DocumentValidator()
validator.load_model()
print()

results_summary = []

# --- TEST 1: BNMIT Image - Format CNN should predict BNMIT ---
print("=" * 60)
print("TEST 1: Format classifier on BNMIT image")
print("=" * 60)
bnmit_dir = "data/B.N.M INSTITUTE OF TECHNOLOGY"
bnmit_img = next(f for f in sorted(os.listdir(bnmit_dir)) if f.startswith("train_") and f.endswith(".jpg"))
img_path = os.path.join(bnmit_dir, bnmit_img)
print(f"  Image: {bnmit_img}")

result = validator.validate(img_path)
fp = result["format_prediction"]
cnn = result["cnn_result"]
flags = result["flags"]

ok1 = all([
    check(fp["is_available"], "Format classifier is_available=True"),
    check(fp["institution"] == "BNMIT", f"Predicted institution=BNMIT (got={fp['institution']}, conf={fp['confidence']:.3f})"),
    check(0.0 <= fp["confidence"] <= 1.0, f"Confidence in range [0,1] (got={fp['confidence']:.3f})"),
    check(isinstance(fp["scores"], dict) and len(fp["scores"]) == 4, f"Scores dict has 4 classes (got={list(fp['scores'].keys())})"),
    check("requires_manual_review" in flags, "flags has requires_manual_review key"),
    check("format_mismatch" in flags, "flags has format_mismatch key"),
    check("potential_forgery" in flags, "flags has potential_forgery key"),
    check(isinstance(cnn["score"], float), f"CNN score is float (got={cnn['score']:.4f})"),
])
results_summary.append(("TEST 1: BNMIT format classification", ok1))

# --- TEST 2: SPPU Image - Format CNN should predict SPPU -----
print()
print("=" * 60)
print("TEST 2: Format classifier on SPPU image")
print("=" * 60)
sppu_dir = "data/SPPU"
sppu_imgs = sorted([f for f in os.listdir(sppu_dir)
                    if not os.path.isdir(os.path.join(sppu_dir, f))
                    and f.lower().endswith((".jpg", ".jpeg", ".webp", ".png"))])
if sppu_imgs:
    img_path2 = os.path.join(sppu_dir, sppu_imgs[0])
    print(f"  Image: {sppu_imgs[0]}")
    result2 = validator.validate(img_path2)
    fp2 = result2["format_prediction"]
    ok2 = all([
        check(fp2["is_available"], "Format classifier is_available=True"),
        check(fp2["institution"] == "SPPU", f"Predicted institution=SPPU (got={fp2['institution']}, conf={fp2['confidence']:.3f})"),
    ])
    results_summary.append(("TEST 2: SPPU format classification", ok2))
else:
    print("  SKIP: No SPPU images found")
    results_summary.append(("TEST 2: SPPU format classification", None))

# --- TEST 3: Format mismatch detection -----------------------
print()
print("=" * 60)
print("TEST 3: Format mismatch flag (BNMIT layout + SPPU text claim)")
print("=" * 60)
r = PipelineResult()
r.format_prediction = {"institution": "BNMIT", "confidence": 0.95, "scores": {}, "is_available": True}
r.ocr_result = ExtractionResult(fields={"institution": "SPPU"})
r.institution_recognition.university_name = "Savitribai Phule Pune University"
flags3 = DocumentValidator._compute_flags(r)
print(f"  flags: {flags3}")
ok3 = all([
    check(flags3["format_mismatch"] is True, "format_mismatch=True detected"),
    check(flags3["potential_forgery"] is True, "potential_forgery=True raised"),
])
results_summary.append(("TEST 3: Format mismatch detection", ok3))

# --- TEST 4: Same institution - no mismatch ------------------
print()
print("=" * 60)
print("TEST 4: No mismatch when format matches claimed institution")
print("=" * 60)
r2 = PipelineResult()
r2.format_prediction = {"institution": "BNMIT", "confidence": 0.95, "scores": {}, "is_available": True}
r2.ocr_result = ExtractionResult(fields={"institution": "BNM Institute"})
r2.institution_recognition.university_name = "B.N.M Institute of Technology"
flags4 = DocumentValidator._compute_flags(r2)
print(f"  flags: {flags4}")
ok4 = all([
    check(flags4["format_mismatch"] is False, "format_mismatch=False (correct match)"),
])
results_summary.append(("TEST 4: True match - no mismatch flag", ok4))

# --- TEST 5: Pipeline result serialisation -------------------
print()
print("=" * 60)
print("TEST 5: PipelineResult.to_dict() serialises format_prediction")
print("=" * 60)
r3 = PipelineResult(request_id="test-123", timestamp="2026-01-01T00:00:00Z")
r3.format_prediction = {"institution": "BNMIT", "confidence": 0.99, "scores": {}, "is_available": True}
d = r3.to_dict()
ok5 = all([
    check("format_prediction" in d, "format_prediction key present in to_dict()"),
    check(d["format_prediction"]["institution"] == "BNMIT", "institution value preserved"),
    check("flags" in d and "format_mismatch" in d["flags"], "format_mismatch flag in serialised flags"),
    check(d["request_id"] == "test-123", "request_id preserved"),
])
results_summary.append(("TEST 5: PipelineResult serialisation", ok5))

# --- SUMMARY -------------------------------------------------
print()
print("=" * 60)
print("INTEGRATION TEST SUMMARY")
print("=" * 60)
all_passed = True
for name, ok in results_summary:
    if ok is None:
        print(f"  {SKIP} {name}")
    else:
        status = PASS if ok else FAIL
        print(f"  {status}: {name}")
        if not ok:
            all_passed = False

print()
if all_passed:
    print("ALL INTEGRATION TESTS PASSED")
    sys.exit(0)
else:
    print("SOME TESTS FAILED -- check output above")
    sys.exit(1)
