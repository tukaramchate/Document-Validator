"""
PyTorch CNN Training Script for Document Forge Detection.
Trains a binary classifier (Real vs Fake) using the data/ directory.
Saves the final model to saved_models/document_cnn_v1.pth
"""
import os
import sys
import time
import copy
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

# ─── Configuration ───────────────────────────────────────────────
IMG_SIZE = 224
BATCH_SIZE = 16
NUM_EPOCHS = 30
LEARNING_RATE = 0.001
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ─── Data Transforms ────────────────────────────────────────────
train_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

val_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])


# ─── Custom CNN Architecture (matches the TF version) ───────────
class ForgeCNN(nn.Module):
    """4-block CNN for binary classification, mirroring architecture.py"""
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
            # Block 2
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
            # Block 3
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.MaxPool2d(2),
            # Block 4
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


def build_transfer_model():
    """ResNet18 transfer learning model for small datasets."""
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    # Freeze all layers
    for param in model.parameters():
        param.requires_grad = False
    # Replace the final FC layer for binary classification
    model.fc = nn.Sequential(
        nn.Linear(model.fc.in_features, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, 1),
    )
    return model


# ─── Training Loop ──────────────────────────────────────────────
def train_model(data_dir, output_path, epochs=NUM_EPOCHS, batch_size=BATCH_SIZE, use_transfer=True):
    print(f"Device: {DEVICE}")
    print(f"Data directory: {data_dir}")
    print(f"Output model: {output_path}")

    # ── Prepare Datasets ────────────────────────────────────────
    full_dataset = datasets.ImageFolder(data_dir, transform=train_transforms)
    class_names = full_dataset.classes
    print(f"Classes found: {class_names}")
    print(f"Total images: {len(full_dataset)}")

    # Split 80/20 train/val
    total = len(full_dataset)
    val_size = max(1, int(0.2 * total))
    train_size = total - val_size
    train_ds, val_ds = torch.utils.data.random_split(full_dataset, [train_size, val_size])

    # Override val transforms (no augmentation)
    val_ds.dataset = copy.copy(full_dataset)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)

    print(f"Training samples: {train_size}, Validation samples: {val_size}")

    # ── Build Model ─────────────────────────────────────────────
    if use_transfer:
        print("Using Transfer Learning (ResNet18)...")
        model = build_transfer_model()
    else:
        print("Using Custom CNN...")
        model = ForgeCNN()

    model = model.to(DEVICE)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)

    # ── Train ───────────────────────────────────────────────────
    best_acc = 0.0
    best_model_wts = copy.deepcopy(model.state_dict())
    patience_counter = 0
    patience_limit = 10

    for epoch in range(epochs):
        start = time.time()

        # Training phase
        model.train()
        running_loss, running_correct = 0.0, 0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(DEVICE), labels.float().to(DEVICE)
            optimizer.zero_grad()
            outputs = model(inputs).squeeze(1)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            preds = (torch.sigmoid(outputs) >= 0.5).float()
            running_correct += (preds == labels).sum().item()

        train_loss = running_loss / train_size
        train_acc = running_correct / train_size

        # Validation phase
        model.eval()
        val_loss, val_correct = 0.0, 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(DEVICE), labels.float().to(DEVICE)
                outputs = model(inputs).squeeze(1)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * inputs.size(0)
                preds = (torch.sigmoid(outputs) >= 0.5).float()
                val_correct += (preds == labels).sum().item()

        val_loss /= val_size
        val_acc = val_correct / val_size
        scheduler.step(val_loss)

        elapsed = time.time() - start
        print(f"Epoch {epoch+1:02d}/{epochs} | "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
              f"Time: {elapsed:.1f}s")

        # Save best
        if val_acc > best_acc:
            best_acc = val_acc
            best_model_wts = copy.deepcopy(model.state_dict())
            patience_counter = 0
        else:
            patience_counter += 1

        if patience_counter >= patience_limit:
            print(f"Early stopping triggered at epoch {epoch+1}")
            break

    # ── Save ────────────────────────────────────────────────────
    model.load_state_dict(best_model_wts)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    torch.save({
        'model_state_dict': best_model_wts,
        'class_names': class_names,
        'architecture': 'resnet18_transfer' if use_transfer else 'custom_cnn',
        'best_val_accuracy': best_acc,
    }, output_path)
    print(f"\n✅ Best model saved to {output_path} (Val Accuracy: {best_acc:.4f})")
    return model


# ─── Entry Point ────────────────────────────────────────────────
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='data', help='Path to data directory')
    parser.add_argument('--output', type=str, default='saved_models/document_cnn_v1.pth', help='Output model path')
    parser.add_argument('--epochs', type=int, default=30)
    parser.add_argument('--batch', type=int, default=16)
    parser.add_argument('--transfer', action='store_true', default=True, help='Use transfer learning')
    parser.add_argument('--custom', action='store_true', help='Use custom CNN instead of transfer learning')
    args = parser.parse_args()

    use_transfer = not args.custom
    train_model(args.data, args.output, args.epochs, args.batch, use_transfer)
