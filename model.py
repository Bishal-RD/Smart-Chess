import torch.nn as nn

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