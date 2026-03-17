# We use tensorflow's ImageDataGenerator for augmentation
import tensorflow as tf

def get_training_augmentation(validation_split=0.2):
    """
    Returns an ImageDataGenerator configured for training data augmentation.
    This creates slight variations to make the CNN more robust.
    """
    return tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255,           # Normalization
        rotation_range=15,        # Handle slightly tilted scans
        width_shift_range=0.1,    # Horizontal translation
        height_shift_range=0.1,   # Vertical translation
        zoom_range=0.1,           # Handle different scan distances
        brightness_range=[0.8, 1.2], # Handle different scan qualities
        horizontal_flip=True,     # Mirror variations
        fill_mode='nearest',      # Fill pixels during rotation/shift
        validation_split=validation_split
    )

def get_validation_augmentation(validation_split=0.2):
    """
    Returns an ImageDataGenerator for validation data.
    Only applies normalization, no random augmentation.
    """
    return tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255,           # Normalization only
        validation_split=validation_split
    )
