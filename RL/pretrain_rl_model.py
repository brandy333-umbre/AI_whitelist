
import numpy as np
import torch
import torch.nn as nn
import sqlite3
import logging
from typing import List, Tuple
import time
from rl_filter import RLFilter, URLFeatureExtractor
import os
import json
from sklearn.model_selection import train_test_split


with open(os.path.join(os.path.dirname(__file__), "rl_pretraining_data.json"), "r") as f: #os.join path ... just makes it such that both files can coordinate together, r just open the data in reading mode, and f is a short name for file
    rl_pretraining_data = json.load(f)

print(f"Total examples loaded: {len(rl_pretraining_data['examples'])}")
print("First sample keys:", rl_pretraining_data['examples'][0].keys())

feature_extractor = URLFeatureExtractor()

all_features = []
all_labels = []


for i, example in enumerate(rl_pretraining_data['examples']):
    features = feature_extractor.extract_features(example['url'], example['mission'])
    all_features.append(features)

    label = example.get('label')
    all_labels.append(label)

print(f"processed {len(all_features)} examples")
print(f"feature vector size: {all_features[0].shape} examples")
print(f"Labels: {np.sum(all_labels)} productive, {len(all_labels) - np.sum(all_labels)} distracting")

features_tensor = torch.tensor(np.array(all_features), dtype=torch.float32)
label_tensor = torch.tensor(all_labels, dtype=torch.float32)

print(f"features tensor shape: {features_tensor.shape}")
print(f"labels tensor shape: {label_tensor.shape}")

# Split data into training and testing sets (80/20 split)
X_train, X_test, y_train, y_test = train_test_split(
    features_tensor, label_tensor, 
    test_size=0.2,     # 20% for testing
    random_state=42,   # Reproducible results
    stratify=label_tensor  # Keep same ratio of productive/distracting in both sets
)

print(f"Training set: {X_train.shape[0]} examples")
print(f"Testing set: {X_test.shape[0]} examples")

class ProductivityClassifier(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.fc1(x))      # Input → Layer 1 → ReLU activation, (changes negatives to 0)
        x = self.dropout(x)             # sets some elements to 0 to prevent overfitting
        x = self.relu(self.fc2(x))      # Layer 1 → Layer 2 → ReLU activation  
        x = self.dropout(x)             # Apply dropout (training only)
        x = self.relu(self.fc3(x))      # Layer 2 → Layer 3 → ReLU activation
        x = self.sigmoid(self.fc4(x))   # Layer 3 → Output → Sigmoid (0-1 probability)
        return x

# Create the model
input_size = features_tensor.shape[1]  # Number of features per example
model = ProductivityClassifier(input_size)
print(f"Model created with input size: {input_size}")

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)#Adam is a type of optimizer that helps the model learn faster and more efficiently
loss_function = nn.BCELoss() #for each prediction measure how wrong the models prediction is
epochs = 10 #an epoch is a full pass through the training data
batch_size = 32 #how many examples to process at once

print(f"Training model for {epochs} epochs with batch size {batch_size}") #the f at the beginning just allows you to include variables with curly brackets

# Track best model
best_test_loss = float('inf')
best_model_state = None

#training loop
for epoch in range(epochs):
    model.train() #activates dropout layers and enables gradient calculation, sets behaviour
    total_loss = 0 #accumulates loss over the epoch

    #process data in batches (use training data only)
    num_batches = len(X_train) // batch_size
    for batch_idx, i in enumerate(range(0, len(X_train), batch_size)): #range(start, stop, step)
        batch_features = X_train[i:i+batch_size] #splits the features into batches of size batch_size
        batch_labels = y_train[i:i+batch_size] #splits the labels into batches of size batch_size

        #forward pass
        predictions = model(batch_features) #feeds 32 examples through the nueral network, outputs 32 predictions
        loss = loss_function(predictions.squeeze(), batch_labels) #calculates the loss between the predictions and the actual labels

        #backward pass
        optimizer.zero_grad()#resets the gradient, which is just a volatile calculation
        loss.backward()#uses backpropagation to calculate the gradient of the loss function with respect to the model parameters
        optimizer.step()#updates the model parameters based on the gradient
         
        total_loss += loss.item()
        
        # Show progress every 1000 batches
        if (batch_idx + 1) % 1000 == 0:
            print(f"    Batch {batch_idx + 1}/{num_batches}, Current Loss: {loss.item():.4f}")

    avg_loss = total_loss / (len(X_train) / batch_size)
    
    # Test on testing data (no training, just evaluation)
    model.eval()  # Turn off dropout for testing
    with torch.no_grad():  # Don't calculate gradients for testing
        test_predictions = model(X_test)
        test_loss = loss_function(test_predictions.squeeze(), y_test)
        
        # Calculate accuracy
        predicted_labels = (test_predictions.squeeze() > 0.5).float()
        accuracy = (predicted_labels == y_test).float().mean()
    
    print(f"Epoch [{epoch+1}/{epochs}], Train Loss: {avg_loss:.4f}, Test Loss: {test_loss:.4f}, Test Accuracy: {accuracy:.4f}")
    
    # Save best model based on test loss
    if test_loss < best_test_loss:
        best_test_loss = test_loss
        best_model_state = model.state_dict().copy()
        print(f"    → New best model! Test loss: {test_loss:.4f}")

print("Training completed!")

# Save the best model (not just the final one)
if best_model_state is not None:
    torch.save(best_model_state, os.path.join(os.path.dirname(__file__), "best_pretrained_model.pth"))
    print(f"Best model saved with test loss: {best_test_loss:.4f}")

# Save final model too
torch.save(model.state_dict(), os.path.join(os.path.dirname(__file__), "final_pretrained_model.pth"))
print("Final model also saved as 'final_pretrained_model.pth'")

# Final summary
print(f"\nTraining Summary:")
print(f"- Total epochs: {epochs}")
print(f"- Training examples: {len(X_train):,}")
print(f"- Testing examples: {len(X_test):,}")
print(f"- Best test loss: {best_test_loss:.4f}")
print(f"- Final test accuracy: {accuracy:.4f}")
print(f"- Model saved: best_pretrained_model.pth")