import numpy as np
import pickle
import tensorflow as tf
from tensorflow.keras import layers, models
from tqdm.keras import TqdmCallback  # Import TqdmCallback for progress tracking

# Ensure GPU is used
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print("GPU memory growth enabled.")
    except RuntimeError as e:
        print(e)
else:
    print("No GPU detected. Training will use the CPU.")

if __name__ == "__main__":
    # Load preprocessed dataset
    dataset_file = "C:/Users/User/Desktop/AI/Projects/Smart-Chess/model_training/Datasets/split_data.pkls"
    try:
        with open(dataset_file, "rb") as file:
            data = pickle.load(file)
            X_train = data["X_train"]
            X_test = data["X_test"]
            y_train = data["y_train"]
            y_test = data["y_test"]
            print("Datasets loaded successfully from .pkl file!")
    except FileNotFoundError:
        print("Dataset file not found. Please preprocess the data and save it as a .pkl file.")
        exit(1)

    # Define the model
    model = models.Sequential([
        layers.Conv2D(64, (3, 3), activation="relu", input_shape=(8, 8, 12)),
        layers.Conv2D(64, (3, 3), activation="relu"),
        layers.Flatten(),
        layers.Dense(128, activation="relu"),
        layers.Dense(1, activation="sigmoid")  # Output: win probability
    ])

    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])

    # Train the model with tqdm progress bar
    print("Starting training on GPU...")
    history = model.fit(
        X_train,
        y_train,
        epochs=10,
        batch_size=64,
        validation_split=0.1,
        callbacks=[TqdmCallback(verbose=1)]  # Add TqdmCallback to monitor progress
    )

    # Evaluate the model
    test_loss, test_accuracy = model.evaluate(X_test, y_test)
    print(f"Test Accuracy: {test_accuracy}")

    # Save the trained model
    model.save("models/chess_evaluation_model.h5")
    print("Model saved as 'chess_evaluation_model.h5'.")
