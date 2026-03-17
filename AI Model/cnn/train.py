import os
import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from architecture import build_cnn_model, build_transfer_learning_model

import sys
import pathlib
# Add parent dir to path to import preprocessing
_BASE_DIR = pathlib.Path(__file__).parent.parent
sys.path.append(str(_BASE_DIR))
from preprocessing.augmentation import get_training_augmentation, get_validation_augmentation

def train_model(data_dir, output_model_path, epochs=50, batch_size=32, use_transfer_learning=False):
    """
    Trains the CNN model using images in the data directory.
    Assumes data_dir contains 'real' and 'fake' subfolders.
    """
    real_dir = os.path.join(data_dir, 'real')
    fake_dir = os.path.join(data_dir, 'fake')
    
    if not os.path.exists(real_dir) or not os.path.exists(fake_dir):
        raise ValueError(f"Data directory {data_dir} must contain 'real' and 'fake' subdirectories")
        
    print("Preparing data generators...")
    train_datagen = get_training_augmentation(validation_split=0.2)
    val_datagen = get_validation_augmentation(validation_split=0.2)
    
    train_generator = train_datagen.flow_from_directory(
        directory=data_dir,
        target_size=(224, 224),
        class_mode='binary',
        batch_size=batch_size,
        subset='training'
    )
    
    validation_generator = val_datagen.flow_from_directory(
        directory=data_dir,
        target_size=(224, 224),
        class_mode='binary',
        batch_size=batch_size,
        subset='validation'
    )
    
    # Check if we have enough data to actually train
    if train_generator.samples == 0:
         raise ValueError(f"No training images found in {data_dir}. Please add images to 'real' and 'fake' folders.")
    
    print(f"Class indices: {train_generator.class_indices}")

    if use_transfer_learning:
        model = build_transfer_learning_model()
    else:
        model = build_cnn_model()
        
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
    )
    
    # Setup callbacks
    os.makedirs(os.path.dirname(output_model_path), exist_ok=True)
    
    callbacks = [
        EarlyStopping(patience=10, restore_best_weights=True, monitor='val_accuracy'),
        ModelCheckpoint(output_model_path, save_best_only=True, monitor='val_accuracy'),
        ReduceLROnPlateau(patience=5, factor=0.5, monitor='val_loss')
    ]
    
    print("Starting training...")
    history = model.fit(
        train_generator,
        epochs=epochs,
        validation_data=validation_generator,
        callbacks=callbacks
    )
    
    print(f"Training complete. Best model saved to {output_model_path}")
    return history

if __name__ == '__main__':
    # Default execution when run directly
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='../data/', help='Path to data directory (with real/ and fake/ subdirs)')
    parser.add_argument('--output', type=str, default='../models/document_cnn_v1.h5', help='Path to save the trained model')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch', type=int, default=32)
    parser.add_argument('--transfer', action='store_true', help='Use transfer learning (ResNet50V2)')
    
    args = parser.parse_args()
    
    try:
        train_model(args.data, args.output, args.epochs, args.batch, args.transfer)
    except Exception as e:
        print(f"Error during training: {e}")
