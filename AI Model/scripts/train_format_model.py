"""
Training Script — Institution-Specific Format Classifier CNN.

Architecture:  ResNet-18 with transfer learning (ImageNet pretrained).
Task:          Multi-class classification — identify WHICH institution a
               document belongs to based purely on its visual layout/format.
Loss:          CrossEntropyLoss (multi-class).
Output:        saved_models/format_classifier_v1.pth
               saved_models/format_classes.json  (class_idx -> institution name)

Usage:
    python scripts/train_format_model.py
    python scripts/train_format_model.py --epochs 50 --lr 0.0001
    python scripts/train_format_model.py --data data/prepared --output saved_models/format_classifier_v1.pth
"""

from __future__ import annotations

import argparse
import json
import os
import time
import copy
import warnings

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import datasets, transforms, models

warnings.filterwarnings("ignore")

# ─── Defaults ────────────────────────────────────────────────
DEFAULT_DATA    = os.path.join(os.path.dirname(__file__), "..", "data", "prepared")
DEFAULT_OUTPUT  = os.path.join(os.path.dirname(__file__), "..", "saved_models", "format_classifier_v1.pth")
DEFAULT_CLASSES = os.path.join(os.path.dirname(__file__), "..", "saved_models", "format_classes.json")

IMG_SIZE     = 224
DEVICE       = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ─── Augmentation transforms ────────────────────────────────
def get_transforms(train: bool):
    mean = [0.485, 0.456, 0.406]
    std  = [0.229, 0.224, 0.225]

    if train:
        return transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.RandomCrop(IMG_SIZE),
            transforms.RandomHorizontalFlip(p=0.3),
            transforms.RandomVerticalFlip(p=0.1),
            transforms.RandomRotation(5),
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.1),
            transforms.RandomGrayscale(p=0.05),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
        ])
    else:
        return transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
        ])


def build_model(num_classes: int) -> nn.Module:
    """ResNet-18 with pretrained ImageNet weights fine-tuned for num_classes."""
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

    # Unfreeze last 2 ResNet blocks for better fine-tuning on small datasets
    for name, param in model.named_parameters():
        if "layer3" in name or "layer4" in name or "fc" in name:
            param.requires_grad = True
        else:
            param.requires_grad = False

    # Replace classifier head
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


def make_weighted_sampler(dataset) -> WeightedRandomSampler:
    """Class-balanced sampler — critical for imbalanced datasets."""
    class_counts = [0] * len(dataset.classes)
    for _, label in dataset.samples:
        class_counts[label] += 1

    weights_per_class = [1.0 / max(c, 1) for c in class_counts]
    sample_weights = [weights_per_class[label] for _, label in dataset.samples]

    return WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True,
    )


def train(
    data_dir: str,
    output_path: str,
    classes_path: str,
    epochs: int,
    batch_size: int,
    lr: float,
    val_split: float,
    patience: int,
) -> None:
    print(f"\n{'='*60}")
    print(f"  Institution Format Classifier — Training")
    print(f"{'='*60}")
    print(f"  Device:      {DEVICE}")
    print(f"  Data:        {data_dir}")
    print(f"  Output:      {output_path}")
    print(f"  Epochs:      {epochs}  |  Batch: {batch_size}  |  LR: {lr}")
    print(f"{'='*60}\n")

    # ── Validate data directory ──────────────────────────────
    if not os.path.isdir(data_dir):
        print(f"[ERROR] Data directory not found: {data_dir}")
        print("  → Run: python scripts/prepare_dataset.py  first.")
        return

    classes = sorted([
        d for d in os.listdir(data_dir)
        if os.path.isdir(os.path.join(data_dir, d))
    ])

    if len(classes) < 2:
        print(f"[ERROR] Need at least 2 classes. Found: {classes}")
        return

    num_classes = len(classes)
    print(f"  Classes ({num_classes}): {classes}\n")

    # ── Datasets ─────────────────────────────────────────────
    full_dataset = datasets.ImageFolder(data_dir, transform=get_transforms(train=True))

    # Manual 80/20 split preserving class distribution
    from torch.utils.data import Subset
    import random

    # Group indices by class
    class_indices: dict[int, list[int]] = {i: [] for i in range(num_classes)}
    for idx, (_, label) in enumerate(full_dataset.samples):
        class_indices[label].append(idx)

    train_indices, val_indices = [], []
    for label, indices in class_indices.items():
        random.shuffle(indices)
        split = max(1, int(len(indices) * (1 - val_split)))
        train_indices.extend(indices[:split])
        val_indices.extend(indices[split:])

    train_ds = Subset(full_dataset, train_indices)
    val_ds   = Subset(
        datasets.ImageFolder(data_dir, transform=get_transforms(train=False)),
        val_indices,
    )

    # Class-balanced sampler for training
    train_sampler = None
    train_shuffle = True
    if len(train_indices) > 0:
        # Build a temporary dataset just for the sampler
        tmp = datasets.ImageFolder(data_dir)
        weights_per_class = [1.0 / max(sum(1 for _, l in tmp.samples if l == c), 1)
                              for c in range(num_classes)]
        sample_weights = [weights_per_class[tmp.samples[i][1]] for i in train_indices]
        train_sampler = WeightedRandomSampler(sample_weights, len(sample_weights), replacement=True)
        train_shuffle = False

    train_loader = DataLoader(
        train_ds, batch_size=batch_size,
        sampler=train_sampler, shuffle=train_shuffle,
        num_workers=0, pin_memory=False,
    )
    val_loader = DataLoader(
        val_ds, batch_size=batch_size,
        shuffle=False, num_workers=0,
    )

    print(f"  Train samples: {len(train_indices)}  |  Val samples: {len(val_indices)}")
    for i, cls in enumerate(classes):
        n = sum(1 for _, l in full_dataset.samples if l == i)
        print(f"    [{i}] {cls}: {n} images")
    print()

    # ── Model ────────────────────────────────────────────────
    model = build_model(num_classes).to(DEVICE)

    # Use label smoothing for small datasets (reduces overconfidence)
    criterion  = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer  = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=lr, weight_decay=1e-4,
    )
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-6)

    # ── Training loop ────────────────────────────────────────
    best_acc  = 0.0
    best_wts  = copy.deepcopy(model.state_dict())
    patience_ctr = 0

    for epoch in range(epochs):
        t0 = time.time()

        # Train
        model.train()
        tr_loss, tr_correct, tr_total = 0.0, 0, 0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            tr_loss    += loss.item() * inputs.size(0)
            _, preds    = outputs.max(1)
            tr_correct += (preds == labels).sum().item()
            tr_total   += inputs.size(0)

        # Validate
        model.eval()
        val_loss, val_correct, val_total = 0.0, 0, 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
                outputs = model(inputs)
                loss    = criterion(outputs, labels)
                val_loss    += loss.item() * inputs.size(0)
                _, preds     = outputs.max(1)
                val_correct += (preds == labels).sum().item()
                val_total   += inputs.size(0)

        train_acc = tr_correct  / max(tr_total,  1)
        val_acc   = val_correct / max(val_total, 1)
        train_loss= tr_loss     / max(tr_total,  1)
        val_loss_ = val_loss    / max(val_total, 1)

        scheduler.step()
        elapsed = time.time() - t0

        print(
            f"Epoch {epoch+1:03d}/{epochs} | "
            f"Train Loss: {train_loss:.4f}  Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss_:.4f}  Acc: {val_acc:.4f} | "
            f"LR: {scheduler.get_last_lr()[0]:.2e} | "
            f"Time: {elapsed:.1f}s"
        )

        if val_acc > best_acc:
            best_acc = val_acc
            best_wts = copy.deepcopy(model.state_dict())
            patience_ctr = 0
            print(f"  ✅  New best val accuracy: {best_acc:.4f}")
        else:
            patience_ctr += 1
            if patience_ctr >= patience:
                print(f"\n  Early stopping triggered at epoch {epoch+1}.")
                break

    # ── Save ─────────────────────────────────────────────────
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    model.load_state_dict(best_wts)
    torch.save({
        "model_state_dict":  best_wts,
        "class_names":       classes,
        "num_classes":       num_classes,
        "architecture":      "resnet18_format_classifier",
        "best_val_accuracy": best_acc,
        "img_size":          IMG_SIZE,
    }, output_path)
    print(f"\n  Model saved → {output_path}")

    # Save class mapping JSON
    class_map = {str(i): cls for i, cls in enumerate(classes)}
    with open(classes_path, "w") as f:
        json.dump({
            "class_map":    class_map,
            "num_classes":  num_classes,
            "best_val_acc": round(best_acc, 4),
        }, f, indent=2)
    print(f"  Class map    → {classes_path}")

    print(f"\n{'='*60}")
    print(f"  TRAINING COMPLETE")
    print(f"  Best Val Accuracy: {best_acc:.4f} ({best_acc*100:.1f}%)")
    print(f"  Classes: {classes}")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Institution Format Classifier.")
    parser.add_argument("--data",    default=DEFAULT_DATA,    help="Path to prepared data directory")
    parser.add_argument("--output",  default=DEFAULT_OUTPUT,  help="Output .pth model path")
    parser.add_argument("--classes", default=DEFAULT_CLASSES, help="Output class map JSON path")
    parser.add_argument("--epochs",  type=int,   default=60,   help="Number of training epochs")
    parser.add_argument("--batch",   type=int,   default=16,   help="Batch size")
    parser.add_argument("--lr",      type=float, default=5e-4, help="Learning rate")
    parser.add_argument("--val",     type=float, default=0.20, help="Validation split fraction")
    parser.add_argument("--patience",type=int,   default=15,   help="Early stopping patience")
    args = parser.parse_args()

    train(
        data_dir=args.data,
        output_path=args.output,
        classes_path=args.classes,
        epochs=args.epochs,
        batch_size=args.batch,
        lr=args.lr,
        val_split=args.val,
        patience=args.patience,
    )
