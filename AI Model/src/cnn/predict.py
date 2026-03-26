"""
PyTorch-based prediction module for Document Forge Detection.
Loads the trained model from saved_models/ and runs inference on a single image.
"""
import os
import random
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image

# ─── Poppler path from environment (P2 fix) ──────────────────────
_DEFAULT_POPPLER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "poppler", "Library", "bin"
)
POPPLER_PATH = os.getenv("POPPLER_PATH", _DEFAULT_POPPLER)

# ─── Production mode guard (P2 fix) ──────────────────────────────
APP_ENV = os.getenv("APP_ENV", "development")


# ─── Model Architecture (must match train_pytorch.py) ───────────
def _build_transfer_model():
    model = models.resnet18(weights=None)
    model.fc = nn.Sequential(
        nn.Linear(model.fc.in_features, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, 1),
    )
    return model


class ForgeCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(128, 256, 3, padding=1), nn.BatchNorm2d(256), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(256, 512), nn.ReLU(), nn.Dropout(0.5),
            nn.Linear(512, 256), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(256, 1),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


# ─── Image Transform (must match validation transform) ─────────
_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])


# ─── Predict Function ──────────────────────────────────────────
def predict(image_path, model_path_or_instance='../../saved_models/document_cnn_v1.pth'):
    """
    Runs inference on a single image.

    In development mode: falls back to a mock prediction if model is missing.
    In production mode (APP_ENV=production): raises RuntimeError if model is missing.

    Input:
        image_path: string path to image
        model_path_or_instance: string path to saved .pth model, OR an already loaded model

    Output:
    {
        "score": 0.85,           # 0.0 (fake) to 1.0 (real)
        "label": "real",         # "real" or "fake"
        "confidence": 0.85       # how sure the model is
    }
    """

    # 1. Handle missing model
    if isinstance(model_path_or_instance, str) and not os.path.exists(model_path_or_instance):
        if APP_ENV == "production":
            # P2 fix: never silently mock in production
            raise RuntimeError(
                f"CNN model not found at '{model_path_or_instance}'. "
                "Cannot serve predictions in production mode. "
                "Either train the model or set APP_ENV=development."
            )
        print(f"WARNING: Model not found at '{model_path_or_instance}'. Using mock prediction.")
        score = round(random.uniform(0.60, 0.95), 4)
        return {
            "score": score,
            "label": "real" if score >= 0.50 else "fake",
            "confidence": score if score >= 0.50 else float(1 - score),
            "is_mock": True
        }

    # 2. Load model
    device = torch.device("cpu")

    if isinstance(model_path_or_instance, str):
        checkpoint = torch.load(model_path_or_instance, map_location=device, weights_only=False)
        arch = checkpoint.get('architecture', 'resnet18_transfer')
        class_names = checkpoint.get('class_names', ['fake', 'real'])

        if arch == 'resnet18_transfer':
            model = _build_transfer_model()
        else:
            model = ForgeCNN()

        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(device)
        model.eval()
    else:
        model = model_path_or_instance
        class_names = ['fake', 'real']

    # 3. Preprocess image
    try:
        if str(image_path).lower().endswith('.pdf'):
            from pdf2image import convert_from_path
            pages = convert_from_path(image_path, poppler_path=POPPLER_PATH)
            if not pages:
                raise ValueError("No pages found in PDF")
            image = pages[0].convert('RGB')
        else:
            image = Image.open(image_path).convert('RGB')

        input_tensor = _transform(image).unsqueeze(0).to(device)
    except Exception as e:
        return {"error": f"Failed to preprocess image: {e}"}

    # 4. Run inference
    with torch.no_grad():
        output = model(input_tensor).squeeze()
        probability = torch.sigmoid(output).item()

    # class_names[0] = 'fake', class_names[1] = 'real'
    score = float(probability)

    return {
        "score": score,
        "label": "real" if score >= 0.50 else "fake",
        "confidence": score if score >= 0.50 else float(1 - score),
        "is_mock": False
    }
