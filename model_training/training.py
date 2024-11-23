import pickle
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm

# Ensure GPU is used if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

class ChessEvaluationModel(nn.Module):
    def __init__(self):
        super(ChessEvaluationModel, self).__init__()
        self.conv1 = nn.Conv2d(12, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool2d(2, 2)  # Down-sample by 2x
        self.flatten = nn.Flatten()
        self.fc1 = nn.Linear(64 * 4 * 4, 128)  # Adjust input size based on pooling
        self.fc2 = nn.Linear(128, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.pool(self.relu(self.conv2(x)))
        x = self.flatten(x)
        x = self.relu(self.fc1(x))
        x = self.sigmoid(self.fc2(x))
        return x

if __name__ == "__main__":
    # Load preprocessed dataset
    dataset_file = "C:/Users/User/Desktop/AI/Projects/Smart-Chess/model_training/Datasets/split_data_10k.pkl"
    try:
        with open(dataset_file, "rb") as file:
            data = pickle.load(file)
            X_train = torch.tensor(data["X_train"], dtype=torch.float32).permute(0, 3, 1, 2).to(device)  # Convert to (N, C, H, W)
            X_test = torch.tensor(data["X_test"], dtype=torch.float32).permute(0, 3, 1, 2).to(device)    # Convert to (N, C, H, W)
            y_train = torch.tensor(data["y_train"], dtype=torch.float32).to(device).view(-1, 1)  # Convert labels to shape (N, 1)
            y_test = torch.tensor(data["y_test"], dtype=torch.float32).to(device).view(-1, 1)
            print("Datasets loaded successfully from .pkl file!")
    except FileNotFoundError:
        print("Dataset file not found. Please preprocess the data and save it as a .pkl file.")
        exit(1)

    # Create DataLoader for batching
    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

    # Define the model
    model = ChessEvaluationModel().to(device)
    criterion = nn.BCELoss()  # Binary Cross-Entropy Loss
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Train the model
    num_epochs = 100
    print("Starting training...")
    for epoch in range(num_epochs):
        model.train()
        epoch_loss = 0
        with tqdm(train_loader, desc=f"Epoch {epoch + 1}/{num_epochs}") as t:
            for X_batch, y_batch in t:
                optimizer.zero_grad()
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
                t.set_postfix(loss=loss.item())
        print(f"Epoch {epoch + 1} Loss: {epoch_loss / len(train_loader):.4f}")
        if(epoch % 10 == 0):
            torch.save(model.state_dict(), f"C:/Users/User/Desktop/AI/Projects/Smart-Chess/models/model_{epoch}.pth")

    # Evaluate the model
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            outputs = model(X_batch)
            predicted = (outputs > 0.5).float()  # Binary classification threshold
            correct += (predicted == y_batch).sum().item()
            total += y_batch.size(0)

    accuracy = correct / total
    print(f"Test Accuracy: {accuracy:.4f}")

    # Save the trained model
    torch.save(model.state_dict(), "C:/Users/User/Desktop/AI/Projects/Smart-Chess/models/chess_evaluation_model.pth")
    print("Model saved as 'chess_evaluation_model.pth'.")
