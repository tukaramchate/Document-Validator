# AI Model Implementation Plan — Document-Validator

## Overview

Build the AI-powered document verification pipeline consisting of three sub-systems: **CNN** (visual authenticity detection), **OCR** (text extraction), and **Database Cross-Verification** (factual data matching).

**Current State:** Single `model.py` with an empty `DocumentValidator` class — all methods are `pass` stubs. No trained model, no OCR, no preprocessing.

---

## Target Architecture

```
ai_model/                           # Renamed from "AI Model/" (no spaces)
├── model.py                        # Main DocumentValidator entry point
├── requirements.txt                # AI/ML dependencies
│
├── preprocessing/                  # Image preprocessing pipeline
│   ├── __init__.py
│   ├── image_processor.py          # Resize, normalize, denoise, convert
│   └── augmentation.py             # Training data augmentation
│
├── cnn/                            # Convolutional Neural Network
│   ├── __init__.py
│   ├── architecture.py             # Model definition (Keras layers)
│   ├── train.py                    # Training script
│   ├── predict.py                  # Inference on new images
│   └── evaluate.py                 # Metrics: accuracy, F1, confusion matrix
│
├── ocr/                            # Optical Character Recognition
│   ├── __init__.py
│   ├── text_extractor.py           # OCR engine wrapper (Tesseract / EasyOCR)
│   ├── field_parser.py             # Parse raw text → structured fields
│   └── confidence.py               # OCR confidence scoring
│
├── verification/                   # Database cross-verification
│   ├── __init__.py
│   ├── db_matcher.py               # Compare extracted fields vs DB records
│   └── score_calculator.py         # Combine all scores → final verdict
│
├── models/                         # Saved trained model files
│   └── (generated after training)
│
├── data/                           # Training dataset
│   ├── real/                       # Genuine document images
│   ├── fake/                       # Forged document images
│   └── labels.csv                  # Image filename → label mapping
│
└── tests/                          # Unit tests
    ├── test_preprocessing.py
    ├── test_cnn.py
    └── test_ocr.py
```

---

## Phase 1: Preprocessing Pipeline

### 1.1 Dependencies

```
# requirements.txt
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
tensorflow==2.13.0
opencv-python==4.8.0
Pillow==10.0.0
pytesseract==0.3.10      # or easyocr==1.7.0
matplotlib==3.7.2
```

### 1.2 Image Processor (`preprocessing/image_processor.py`)

Functions:

| Function | Input | Output | Purpose |
|---|---|---|---|
| `load_image(path)` | File path (str) | NumPy array (H×W×3) | Reads image using OpenCV/Pillow |
| `resize(image, size)` | Array, (224,224) | Array (224×224×3) | Standardize dimensions for CNN |
| `normalize(image)` | Array (0–255) | Array (0.0–1.0) | Scale pixel values for neural network |
| `to_grayscale(image)` | Array (H×W×3) | Array (H×W×1) | For OCR processing |
| `denoise(image)` | Array | Array | Gaussian blur or bilateral filter |
| `preprocess_for_cnn(path)` | File path | Array (1,224,224,3) | Full pipeline: load → resize → normalize → batch dim |
| `preprocess_for_ocr(path)` | File path | Array (grayscale) | Full pipeline: load → grayscale → denoise |

### 1.3 Data Augmentation (`preprocessing/augmentation.py`)

Used during training ONLY to artificially expand the dataset:

| Augmentation | Parameters | Purpose |
|---|---|---|
| Random Rotation | ±15 degrees | Handle slightly tilted scans |
| Horizontal Flip | 50% probability | Mirror variations |
| Brightness Shift | ±20% | Handle different scan qualities |
| Zoom | 0.9–1.1× | Handle different scan distances |
| Gaussian Noise | σ = 0.01 | Simulate low-quality scans |
| JPEG Compression | Quality 70–95 | Simulate re-saved/compressed documents |

Implementation uses `tf.keras.preprocessing.image.ImageDataGenerator`:

```python
datagen = ImageDataGenerator(
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.1,
    brightness_range=[0.8, 1.2],
    horizontal_flip=True,
    fill_mode='nearest',
    validation_split=0.2
)
```

---

## Phase 2: CNN Model (Convolutional Neural Network)

### 2.1 Architecture (`cnn/architecture.py`)

Binary classification CNN: Real (1) vs Fake (0)

```
Layer                          Output Shape         Parameters
═══════════════════════════════════════════════════════════════
Input                          (224, 224, 3)         0
───────────────────────────────────────────────────────────────
Conv2D (32 filters, 3×3)       (222, 222, 32)        896
BatchNormalization             (222, 222, 32)        128
ReLU Activation                (222, 222, 32)        0
MaxPooling2D (2×2)             (111, 111, 32)        0
───────────────────────────────────────────────────────────────
Conv2D (64 filters, 3×3)       (109, 109, 64)        18,496
BatchNormalization             (109, 109, 64)        256
ReLU Activation                (109, 109, 64)        0
MaxPooling2D (2×2)             (54, 54, 64)          0
───────────────────────────────────────────────────────────────
Conv2D (128 filters, 3×3)      (52, 52, 128)         73,856
BatchNormalization             (52, 52, 128)         512
ReLU Activation                (52, 52, 128)         0
MaxPooling2D (2×2)             (26, 26, 128)         0
───────────────────────────────────────────────────────────────
Conv2D (256 filters, 3×3)      (24, 24, 256)         295,168
BatchNormalization             (24, 24, 256)         1,024
ReLU Activation                (24, 24, 256)         0
MaxPooling2D (2×2)             (12, 12, 256)         0
───────────────────────────────────────────────────────────────
GlobalAveragePooling2D         (256,)                0
───────────────────────────────────────────────────────────────
Dense (512, ReLU)              (512,)                131,584
Dropout (0.5)                  (512,)                0
Dense (256, ReLU)              (256,)                131,328
Dropout (0.3)                  (256,)                0
Dense (1, Sigmoid)             (1,)                  257
═══════════════════════════════════════════════════════════════
Total Parameters:              ~653,505
Trainable Parameters:          ~652,545
```

**Why this architecture:**
- 4 Conv blocks with increasing filters (32→64→128→256) capture progressively complex patterns
- BatchNormalization stabilizes training and allows higher learning rates
- GlobalAveragePooling replaces Flatten — reduces overfitting, fewer parameters
- Two Dense layers with Dropout for robust classification
- Sigmoid output → probability that document is real (0.0 to 1.0)

### 2.2 Alternative: Transfer Learning Approach

For better accuracy with limited data, use a pre-trained base:

```python
from tensorflow.keras.applications import ResNet50V2

base_model = ResNet50V2(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)
base_model.trainable = False  # Freeze base layers

model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dense(256, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])
```

**When to use Transfer Learning:**
- Dataset has < 1,000 images per class
- Need higher accuracy quickly
- Documents share visual patterns with ImageNet objects (text, textures, edges)

### 2.3 Training Script (`cnn/train.py`)

```
Training Pipeline:
    │
    ├── 1. Load dataset from data/real/ and data/fake/
    │      - Assign labels: real=1, fake=0
    │
    ├── 2. Split data:
    │      - 80% Training
    │      - 10% Validation
    │      - 10% Test (held out until final evaluation)
    │
    ├── 3. Apply augmentation to training set
    │
    ├── 4. Compile model:
    │      - Optimizer: Adam (lr=0.001)
    │      - Loss: Binary Cross-Entropy
    │      - Metrics: Accuracy, AUC
    │
    ├── 5. Train with callbacks:
    │      - EarlyStopping(patience=10, restore_best_weights=True)
    │      - ModelCheckpoint(save_best_only=True)
    │      - ReduceLROnPlateau(patience=5, factor=0.5)
    │
    ├── 6. Training parameters:
    │      - Epochs: 50–100 (early stopping will cut short)
    │      - Batch size: 32
    │      - Input size: 224×224×3
    │
    └── 7. Save model to models/document_cnn_v1.h5
```

### 2.4 Prediction (`cnn/predict.py`)

```python
def predict(image_path):
    """
    Input: path to document image
    Output: {
        "score": 0.85,           # 0.0 (fake) to 1.0 (real)
        "label": "real",         # "real" or "fake"
        "confidence": 0.85       # same as score for binary
    }
    """
    image = preprocess_for_cnn(image_path)
    model = load_model('models/document_cnn_v1.h5')
    prediction = model.predict(image)[0][0]
    return {
        "score": float(prediction),
        "label": "real" if prediction >= 0.5 else "fake",
        "confidence": float(prediction) if prediction >= 0.5 else float(1 - prediction)
    }
```

### 2.5 Evaluation (`cnn/evaluate.py`)

Metrics to compute on the test set:

| Metric | What It Measures | Target |
|---|---|---|
| **Accuracy** | Overall correct predictions / total | ≥ 85% |
| **Precision** | True Positives / (True Positives + False Positives) | ≥ 80% |
| **Recall** | True Positives / (True Positives + False Negatives) | ≥ 80% |
| **F1-Score** | Harmonic mean of Precision and Recall | ≥ 80% |
| **AUC-ROC** | Area under the ROC curve | ≥ 0.85 |
| **Confusion Matrix** | TP, TN, FP, FN counts | Visual inspection |

Outputs:
- Classification report (text)
- Confusion matrix (heatmap plot saved to `models/confusion_matrix.png`)
- ROC curve (plot saved to `models/roc_curve.png`)
- Training history (accuracy/loss curves saved to `models/training_history.png`)

---

## Phase 3: OCR Pipeline (Optical Character Recognition)

### 3.1 OCR Engine Options

| Engine | Pros | Cons |
|---|---|---|
| **Tesseract** (pytesseract) | Free, open-source, 100+ languages, widely used | Requires system install, moderate accuracy |
| **EasyOCR** | Pure Python, GPU support, good accuracy | Larger model download, slower startup |
| **Google Vision API** | Best accuracy, structured output | Paid API, requires internet |

**Recommendation:** Start with **Tesseract** (free, no API cost), upgrade to EasyOCR or Vision API if accuracy is insufficient.

### 3.2 Text Extractor (`ocr/text_extractor.py`)

```python
def extract_text(image_path):
    """
    Input: path to document image
    Output: {
        "raw_text": "Full extracted text...",
        "confidence": 0.87,
        "word_confidences": [
            {"word": "Mumbai", "confidence": 0.95},
            {"word": "University", "confidence": 0.92},
            ...
        ]
    }
    """
    image = preprocess_for_ocr(image_path)
    
    # Tesseract approach:
    data = pytesseract.image_to_data(image, output_type=Output.DICT)
    words = data['text']
    confidences = data['conf']
    
    raw_text = pytesseract.image_to_string(image)
    avg_confidence = mean([c for c in confidences if c > 0]) / 100
    
    return {
        "raw_text": raw_text,
        "confidence": avg_confidence,
        "word_confidences": [...]
    }
```

### 3.3 Field Parser (`ocr/field_parser.py`)

Extracts structured fields from raw OCR text using regex patterns:

```python
FIELD_PATTERNS = {
    "name": [
        r"(?:Name|Student Name|Candidate Name)\s*[:\-]\s*(.+)",
        r"(?:Name of the Student)\s*[:\-]\s*(.+)"
    ],
    "roll_number": [
        r"(?:Roll No|Roll Number|Reg No|Registration No)\s*[:\-]\s*([\w\/\-]+)",
        r"(?:Enrollment No)\s*[:\-]\s*([\w\/\-]+)"
    ],
    "institution": [
        r"([\w\s]+ University)",
        r"([\w\s]+ Institute of Technology)"
    ],
    "date": [
        r"(?:Date|Issued on|Date of Issue)\s*[:\-]\s*([\d\/\-\.]+)"
    ],
    "cgpa": [
        r"(?:CGPA|GPA|Grade Point)\s*[:\-]\s*([\d\.]+)"
    ],
    "degree": [
        r"(?:Degree|Programme|Course)\s*[:\-]\s*(.+)"
    ]
}
```

```python
def parse_fields(raw_text):
    """
    Input: "Mumbai University\nName: Rahul Sharma\nRoll No: 2022CSE1045\nCGPA: 8.5"
    Output: {
        "name": {"value": "Rahul Sharma", "confidence": 0.95},
        "roll_number": {"value": "2022CSE1045", "confidence": 0.92},
        "institution": {"value": "Mumbai University", "confidence": 0.88},
        "cgpa": {"value": "8.5", "confidence": 0.90}
    }
    """
```

---

## Phase 4: Database Cross-Verification

### 4.1 Trusted Records Table Structure

The backend database contains a `trusted_records` table pre-loaded with institutional data:

```
trusted_records:
    id              INTEGER PRIMARY KEY
    institution     VARCHAR(200)      # "Mumbai University"
    record_type     VARCHAR(50)       # "marksheet", "certificate"
    identifier      VARCHAR(100)      # "2022CSE1045" (roll number / ID)
    data            JSON              # {"name": "Rahul Sharma", "cgpa": "7.2", ...}
    created_at      DATETIME
```

### 4.2 Database Matcher (`verification/db_matcher.py`)

```python
def match_against_db(extracted_fields, db_session):
    """
    Input: extracted fields from OCR
    Output: {
        "score": 0.67,                 # matched_fields / total_fields
        "total_fields": 3,
        "matched_fields": 2,
        "details": {
            "name": {
                "extracted": "Rahul Sharma",
                "db_value": "Rahul Sharma",
                "match": True,
                "similarity": 1.0
            },
            "roll_number": {
                "extracted": "2022CSE1045",
                "db_value": "2022CSE1045",
                "match": True,
                "similarity": 1.0
            },
            "cgpa": {
                "extracted": "8.5",
                "db_value": "7.2",
                "match": False,
                "similarity": 0.0
            }
        }
    }
    """
```

### 4.3 Fuzzy String Matching

OCR may produce slightly incorrect characters (e.g., "Rahul Sharrna" instead of "Rahul Sharma"). Use fuzzy matching to handle this:

```python
from difflib import SequenceMatcher

def fuzzy_match(str1, str2, threshold=0.85):
    """
    Returns True if similarity >= threshold
    "Rahul Sharrna" vs "Rahul Sharma" → similarity = 0.92 → match = True
    "8.5" vs "7.2" → similarity = 0.0 → match = False
    """
    similarity = SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    return {
        "match": similarity >= threshold,
        "similarity": round(similarity, 2)
    }
```

---

## Phase 5: Score Calculator & Final Verdict

### 5.1 Score Combination (`verification/score_calculator.py`)

```python
def calculate_final_score(cnn_score, ocr_confidence, db_match_score):
    """
    Weighted scoring formula:
        CNN Visual Analysis:         40% weight
        OCR Extraction Confidence:   20% weight
        Database Match Score:        40% weight
    
    Input:
        cnn_score:      0.85  (CNN predicts 85% chance of being real)
        ocr_confidence: 0.92  (OCR was 92% confident in text extraction)
        db_match_score: 0.60  (2 of 3 fields matched the database)
    
    Calculation:
        final = (0.85 × 0.4) + (0.92 × 0.2) + (0.60 × 0.4)
        final = 0.34 + 0.184 + 0.24
        final = 0.764
    
    Output:
        {
            "final_score": 0.764,
            "verdict": "SUSPICIOUS",
            "breakdown": {
                "cnn_contribution": 0.34,
                "ocr_contribution": 0.184,
                "db_contribution": 0.24
            }
        }
    """
    
    WEIGHTS = {"cnn": 0.4, "ocr": 0.2, "db": 0.4}
    
    final_score = (
        cnn_score * WEIGHTS["cnn"] +
        ocr_confidence * WEIGHTS["ocr"] +
        db_match_score * WEIGHTS["db"]
    )
    
    if final_score >= 0.90:
        verdict = "AUTHENTIC"
    elif final_score >= 0.70:
        verdict = "SUSPICIOUS"
    else:
        verdict = "FAKE"
    
    return {
        "final_score": round(final_score, 3),
        "verdict": verdict,
        "breakdown": {
            "cnn_contribution": round(cnn_score * WEIGHTS["cnn"], 3),
            "ocr_contribution": round(ocr_confidence * WEIGHTS["ocr"], 3),
            "db_contribution": round(db_match_score * WEIGHTS["db"], 3)
        }
    }
```

### 5.2 Verdict Thresholds

| Score Range | Verdict | Color | Meaning |
|---|---|---|---|
| **≥ 0.90** (90%+) | AUTHENTIC | 🟢 Green | Document is very likely genuine |
| **0.70 – 0.89** (70–89%) | SUSPICIOUS | 🟠 Orange | Needs manual review |
| **< 0.70** (<70%) | FAKE | 🔴 Red | Document is likely forged |

---

## Phase 6: Main Entry Point — DocumentValidator

### 6.1 Updated `model.py`

```python
class DocumentValidator:
    def __init__(self, model_path='models/document_cnn_v1.h5'):
        self.cnn_model = None
        self.model_path = model_path
    
    def load_model(self):
        """Load the trained CNN model from disk"""
        self.cnn_model = tf.keras.models.load_model(self.model_path)
    
    def validate(self, image_path, db_session=None):
        """
        Full validation pipeline
        
        Returns: {
            "cnn_result": {"score": 0.85, "label": "real"},
            "ocr_result": {"fields": {...}, "confidence": 0.92},
            "db_result": {"score": 0.60, "matches": {...}},
            "final": {"score": 0.764, "verdict": "SUSPICIOUS"}
        }
        """
        # Step 1: CNN Visual Analysis
        cnn_result = predict(image_path, self.cnn_model)
        
        # Step 2: OCR Text Extraction
        ocr_result = extract_text(image_path)
        parsed_fields = parse_fields(ocr_result["raw_text"])
        
        # Step 3: Database Cross-Verification
        db_result = match_against_db(parsed_fields, db_session)
        
        # Step 4: Score Combination
        final = calculate_final_score(
            cnn_score=cnn_result["score"],
            ocr_confidence=ocr_result["confidence"],
            db_match_score=db_result["score"]
        )
        
        return {
            "cnn_result": cnn_result,
            "ocr_result": {"fields": parsed_fields, "confidence": ocr_result["confidence"]},
            "db_result": db_result,
            "final": final
        }
    
    def train(self, data_dir='data/', epochs=50, batch_size=32):
        """Train the CNN on real/fake dataset"""
        # Calls cnn/train.py
        pass
```

---

## Training Data Requirements

### Minimum Dataset Size

| Category | Minimum | Recommended | Purpose |
|---|---|---|---|
| Real documents | 200 images | 500+ images | Genuine certificates, marksheets, IDs |
| Fake documents | 200 images | 500+ images | Tampered, photoshopped, or synthesized fakes |
| **Total** | **400 images** | **1,000+ images** | Balanced binary classification |

### Data Collection Sources

| Source | Type |
|---|---|
| Scanned certificates | Real |
| Manually created fakes (Photoshop edits) | Fake |
| Synthetically generated documents | Fake |
| Public dataset (if available) | Both |

### Data Organization

```
data/
├── real/
│   ├── marksheet_001.jpg
│   ├── marksheet_002.jpg
│   ├── certificate_001.png
│   └── ...
├── fake/
│   ├── fake_marksheet_001.jpg
│   ├── tampered_cert_001.png
│   └── ...
└── labels.csv
    # filename, label
    # real/marksheet_001.jpg, 1
    # fake/fake_marksheet_001.jpg, 0
```

---

## Implementation Timeline

| Phase | Task | Estimated Time |
|---|---|---|
| Phase 1 | Preprocessing pipeline (image_processor + augmentation) | 3–4 hours |
| Phase 2 | CNN architecture, training, prediction, evaluation | 1–2 weeks |
| Phase 3 | OCR integration (Tesseract + field parser) | 4–6 hours |
| Phase 4 | Database cross-verification (matcher + fuzzy matching) | 3–4 hours |
| Phase 5 | Score calculator + final verdict logic | 2–3 hours |
| Phase 6 | DocumentValidator class + integration with backend | 3–4 hours |
| **Total** | | **2–3 weeks** |

> **Note:** The CNN training time heavily depends on:
> - Dataset size (collection is the bottleneck)
> - GPU availability (CPU training is 10–50× slower)
> - Desired accuracy (more tuning iterations = more time)

---

*Plan prepared: February 22, 2026*
