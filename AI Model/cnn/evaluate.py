import os
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import matplotlib.pyplot import plt

import sys
import pathlib
_BASE_DIR = pathlib.Path(__file__).parent.parent
sys.path.append(str(_BASE_DIR))
from preprocessing.augmentation import get_validation_augmentation

def evaluate_model(data_dir, model_path='../models/document_cnn_v1.h5', batch_size=32):
    """
    Evaluates the trained CNN model on the validation/test data.
    Generates classification report and confusion matrix plot.
    """
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}. Please train first.")
        return
        
    print(f"Loading model from {model_path}...")
    model = tf.keras.models.load_model(model_path)
    
    val_datagen = get_validation_augmentation(validation_split=0.2)
    
    test_generator = val_datagen.flow_from_directory(
        directory=data_dir,
        target_size=(224, 224),
        class_mode='binary',
        batch_size=batch_size,
        subset='validation',
        shuffle=False  # Important for keeping order with true labels!
    )
    
    if test_generator.samples == 0:
        print("No validation data found.")
        return
        
    print("Running predictions...")
    predictions = model.predict(test_generator)
    pred_labels = (predictions > 0.5).astype(int).flatten()
    true_labels = test_generator.classes
    
    print("\n--- Classification Report ---")
    print(classification_report(true_labels, pred_labels, target_names=['fake', 'real']))
    
    print("\n--- AUC-ROC ---")
    auc = roc_auc_score(true_labels, predictions)
    print(f"AUC Score: {auc:.4f}")
    
    # Generate Confusion Matrix Plot
    cm = confusion_matrix(true_labels, pred_labels)
    plot_confusion_matrix(cm, ['fake', 'real'], os.path.join(os.path.dirname(model_path), 'confusion_matrix.png'))
    print(f"Saved confusion matrix plot to {os.path.join(os.path.dirname(model_path), 'confusion_matrix.png')}")

def plot_confusion_matrix(cm, class_names, output_path):
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    plt.colorbar()
    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names, rotation=45)
    plt.yticks(tick_marks, class_names)

    # Label the cells
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(j, i, format(cm[i, j], 'd'),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")

    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default='../data/', help='Path to data directory')
    parser.add_argument('--model', type=str, default='../models/document_cnn_v1.h5', help='Path to trained model')
    args = parser.parse_args()
    
    evaluate_model(args.data, args.model)
