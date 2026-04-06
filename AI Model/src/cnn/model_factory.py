"""
CNN Model Factory.

Factory Pattern implementation for creating and loading CNN model instances.
Provides a single point of control for model architecture selection,
weight loading, and device management.

Supported architectures:
  - resnet18_transfer: ResNet18 with transfer learning (production default).
  - custom_cnn: Custom 4-block CNN (ForgeCNN).
"""
from __future__ import annotations

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
    RESNET18_TRANSFER = "resnet18_transfer"
    CUSTOM_CNN = "custom_cnn"


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


# ─── Factory registry (Open/Closed: register new architectures here) ─────
_MODEL_BUILDERS: dict[ModelArchitecture, Any] = {
    ModelArchitecture.RESNET18_TRANSFER: _build_resnet18_transfer,
    ModelArchitecture.CUSTOM_CNN: ForgeCNN,
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
