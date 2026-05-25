"""
CNN Model Factory.

Factory Pattern implementation for creating and loading CNN model instances.
Provides a single point of control for model architecture selection,
weight loading, and device management.

Supported architectures:
  - resnet18_transfer:        ResNet18 binary forgery detector (production default).
  - custom_cnn:               Custom 4-block CNN (ForgeCNN).
  - resnet18_format_classifier: ResNet18 multi-class institution format classifier.
"""
from __future__ import annotations

import json
import logging
import os
from enum import Enum
from typing import Any

import torch
import torch.nn as nn
from torchvision import models

from src.exceptions import ModelInferenceError, ModelNotFoundError

logger = logging.getLogger(__name__)


class ModelArchitecture(str, Enum):
    """Supported CNN architectures."""
    RESNET18_TRANSFER          = "resnet18_transfer"
    CUSTOM_CNN                 = "custom_cnn"
    FORMAT_CLASSIFIER          = "resnet18_format_classifier"


class ForgeCNN(nn.Module):
    """Custom 4-block CNN for binary forgery classification."""

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

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.classifier(x)
        return x


def _build_resnet18_transfer() -> nn.Module:
    """Build ResNet18 transfer learning model for binary classification."""
    model = models.resnet18(weights=None)
    model.fc = nn.Sequential(
        nn.Linear(model.fc.in_features, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, 1),
    )
    return model


def _build_format_classifier(num_classes: int) -> nn.Module:
    """Build ResNet18 multi-class institution format classifier."""
    model = models.resnet18(weights=None)
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Linear(in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(512, 256),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(256, num_classes),
    )
    return model


# ─── Factory registry (Open/Closed: register new architectures here) ─────
_MODEL_BUILDERS: dict[ModelArchitecture, Any] = {
    ModelArchitecture.RESNET18_TRANSFER: _build_resnet18_transfer,
    ModelArchitecture.CUSTOM_CNN: ForgeCNN,
    # FORMAT_CLASSIFIER uses num_classes arg — instantiated directly in FormatClassifierFactory
}


class CNNModelFactory:
    """
    Factory for creating and loading CNN model instances.

    Usage:
        factory = CNNModelFactory()
        model, class_names = factory.load("saved_models/document_cnn_v1.pth")
        # or
        model = factory.create(ModelArchitecture.RESNET18_TRANSFER)
    """

    def __init__(self, device: torch.device | None = None):
        """
        Args:
            device: Torch device (auto-detected if None).
        """
        self.device = device or torch.device("cpu")

    def create(self, architecture: ModelArchitecture) -> nn.Module:
        """
        Create a new (untrained) model instance.

        Args:
            architecture: Model architecture to instantiate.

        Returns:
            nn.Module in eval mode on the configured device.

        Raises:
            ModelInferenceError: If architecture is not recognized.
        """
        builder = _MODEL_BUILDERS.get(architecture)
        if builder is None:
            raise ModelInferenceError(
                f"Unknown architecture: {architecture}",
                model_name=architecture.value,
            )

        model = builder()
        model.to(self.device)
        model.eval()
        logger.info(f"CNNModelFactory: Created {architecture.value} model on {self.device}")
        return model

    def load(
        self, model_path: str, allow_mock: bool = True
    ) -> tuple[nn.Module | None, list[str], bool]:
        """
        Load a trained model from a checkpoint file.

        Args:
            model_path: Path to .pth checkpoint file.
            allow_mock: If True, returns None when model file is missing
                        (caller should use mock predictions). If False,
                        raises ModelNotFoundError.

        Returns:
            Tuple of (model, class_names, is_mock).
            If model is None, is_mock is True.

        Raises:
            ModelNotFoundError: If allow_mock is False and model file doesn't exist.
            ModelInferenceError: If checkpoint is corrupted.
        """
        if not os.path.exists(model_path):
            if allow_mock:
                logger.warning(
                    f"CNNModelFactory: Model not found at {model_path}. "
                    f"Will use mock predictions."
                )
                return None, ["fake", "real"], True
            raise ModelNotFoundError(model_path)

        try:
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)

            arch_str = checkpoint.get("architecture", "resnet18_transfer")
            class_names = checkpoint.get("class_names", ["fake", "real"])

            try:
                architecture = ModelArchitecture(arch_str)
            except ValueError:
                architecture = ModelArchitecture.RESNET18_TRANSFER

            model = self.create(architecture)
            model.load_state_dict(checkpoint["model_state_dict"])
            model.eval()

            best_acc = checkpoint.get("best_val_accuracy", "unknown")
            logger.info(
                f"CNNModelFactory: Loaded {architecture.value} from {model_path} "
                f"(val_acc={best_acc}, classes={class_names})"
            )

            return model, class_names, False

        except Exception as exc:
            raise ModelInferenceError(
                f"Failed to load model from {model_path}: {exc}",
                model_name=model_path,
            ) from exc

    @staticmethod
    def available_architectures() -> list[str]:
        """List all registered model architectures."""
        return [arch.value for arch in _MODEL_BUILDERS]


# ────────────────────────────────────────────────────────────
# Format Classifier Factory (Institution-Specific Model)
# ────────────────────────────────────────────────────────────

class FormatClassifierFactory:
    """
    Dedicated factory for the Institution Format Classifier model.

    Loads:
      - saved_models/format_classifier_v1.pth   (ResNet-18 multi-class weights)
      - saved_models/format_classes.json         (class_idx -> institution name)

    Usage:
        factory = FormatClassifierFactory()
        factory.load()
        result = factory.predict(pil_image)
        # result = {"institution": "BNMIT", "confidence": 0.9823, "scores": {...}}
    """

    from torchvision import transforms as _transforms

    _TRANSFORM = _transforms.Compose([
        _transforms.Resize((224, 224)),
        _transforms.ToTensor(),
        _transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    DEFAULT_MODEL_PATH   = os.path.join(
        os.path.dirname(__file__), "..", "..", "saved_models", "format_classifier_v1.pth"
    )
    DEFAULT_CLASSES_PATH = os.path.join(
        os.path.dirname(__file__), "..", "..", "saved_models", "format_classes.json"
    )

    def __init__(
        self,
        model_path: str | None = None,
        classes_path: str | None = None,
        device: torch.device | None = None,
    ):
        self.model_path   = model_path   or self.DEFAULT_MODEL_PATH
        self.classes_path = classes_path or self.DEFAULT_CLASSES_PATH
        self.device       = device or torch.device("cpu")

        self._model: nn.Module | None = None
        self._class_map: dict[int, str] = {}
        self._loaded = False

    def load(self, allow_missing: bool = True) -> bool:
        """
        Load the format classifier from disk.

        Args:
            allow_missing: If True, silently skips when model file is absent.
                           If False, raises ModelNotFoundError.

        Returns:
            True if model loaded, False if skipped.
        """
        if not os.path.exists(self.model_path):
            if allow_missing:
                logger.warning(
                    f"FormatClassifierFactory: model not found at {self.model_path}. "
                    "Format verification will be skipped."
                )
                return False
            raise ModelNotFoundError(self.model_path)

        # Load class map
        if os.path.exists(self.classes_path):
            with open(self.classes_path) as f:
                meta = json.load(f)
            self._class_map = {int(k): v for k, v in meta["class_map"].items()}
        else:
            logger.warning("FormatClassifierFactory: class map JSON not found.")
            self._class_map = {}

        # Load model
        try:
            checkpoint   = torch.load(self.model_path, map_location=self.device, weights_only=False)
            num_classes  = checkpoint.get("num_classes", len(self._class_map))
            model        = _build_format_classifier(num_classes)
            model.load_state_dict(checkpoint["model_state_dict"])
            model.to(self.device)
            model.eval()
            self._model  = model
            self._loaded = True

            best_acc = checkpoint.get("best_val_accuracy", "?")
            logger.info(
                f"FormatClassifierFactory: loaded {num_classes}-class model "
                f"(val_acc={best_acc:.4f}, classes={list(self._class_map.values())})"
            )
            return True

        except Exception as exc:
            raise ModelInferenceError(
                f"Failed to load format classifier: {exc}",
                model_name=self.model_path,
            ) from exc

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def classes(self) -> list[str]:
        return list(self._class_map.values())

    def predict(self, image) -> dict[str, Any]:
        """
        Predict which institution's format this document image matches.

        Args:
            image: PIL.Image.Image — the document page (RGB).

        Returns:
            {
                "institution":  "BNMIT",       # top predicted class
                "confidence":   0.9823,         # softmax probability of top class
                "scores":       {"BNMIT": 0.98, "GHRCEM": 0.01, ...},
                "is_available": True,
            }
        """
        if not self._loaded or self._model is None:
            return {
                "institution":  None,
                "confidence":   0.0,
                "scores":       {},
                "is_available": False,
            }

        import torch.nn.functional as F

        try:
            tensor = self._TRANSFORM(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                logits = self._model(tensor)
                probs  = F.softmax(logits, dim=1).squeeze()

            top_idx  = int(probs.argmax().item())
            top_conf = float(probs[top_idx].item())
            scores   = {
                self._class_map.get(i, str(i)): round(float(p), 4)
                for i, p in enumerate(probs.tolist())
            }

            return {
                "institution":  self._class_map.get(top_idx, "unknown"),
                "confidence":   round(top_conf, 4),
                "scores":       scores,
                "is_available": True,
            }

        except Exception as exc:
            logger.error(f"FormatClassifierFactory.predict failed: {exc!r}")
            return {
                "institution":  None,
                "confidence":   0.0,
                "scores":       {},
                "is_available": False,
            }
