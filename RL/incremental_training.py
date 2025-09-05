#!/usr/bin/env python3
"""
Incremental Training Script for Anchorite RL Model
Uses seed data to enhance existing model without losing previous knowledge
"""

import numpy as np
import torch
import torch.nn as nn
import json
import logging
import os
import random
from typing import List, Tuple
from sklearn.model_selection import train_test_split
from rl_filter import URLFeatureExtractor, ProductivityClassifier

class IncrementalTrainer:
    """Incremental trainer that adds seed data to existing model knowledge"""
    
    def __init__(self):
        self.feature_extractor = URLFeatureExtractor()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.input_size = 1186  # Actual feature vector size (384+384+384+15+15+4)
        
        # Training parameters for incremental learning
        self.epochs = 5  # Fewer epochs since we're fine-tuning
        self.batch_size = 32
        self.learning_rate = 0.0001  # Lower learning rate to preserve existing knowledge
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_seed_data(self, seed_file: str = "../anchorite_seed_lists.json") -> dict:
        """Load the seed data from JSON file"""
        try:
            with open(seed_file, 'r', encoding='utf-8') as f:
                seed_data = json.load(f)
            self.logger.info(f"Loaded seed data: {len(seed_data['missions'])} missions, "
                           f"{len(seed_data['educational_channels'])} educational channels, "
                           f"{len(seed_data['entertainment_channels'])} entertainment channels, "
                           f"{len(seed_data['titles'])} titles")
            return seed_data
        except Exception as e:
            self.logger.error(f"Error loading seed data: {e}")
            raise
    
    def generate_training_examples(self, seed_data: dict) -> List[Tuple[dict, str, int]]:
        """Generate training examples from seed data"""
        examples = []
        
        missions = seed_data['missions']
        educational_channels = seed_data['educational_channels']
        entertainment_channels = seed_data['entertainment_channels'] 
        titles = seed_data['titles']
        
        # Create positive examples (productive content)
        self.logger.info("Generating positive examples (educational content)...")
        for i, mission in enumerate(missions[:100]):  # Use first 100 missions
            # Educational YouTube videos
            for _ in range(3):  # 3 examples per mission
                channel = random.choice(educational_channels)
                title = random.choice(titles)
                
                # Create realistic educational URLs
                url_patterns = [
                    f"https://www.youtube.com/watch?v={self._generate_video_id()}",
                    f"https://github.com/{channel.lower().replace(' ', '')}/tutorial-{title.split()[2].lower()}",
                    f"https://docs.{channel.lower().replace(' ', '')}.com/{title.split()[2].lower()}",
                    f"https://{channel.lower().replace(' ', '')}.edu/course/{title.split()[3].lower()}",
                    f"https://stackoverflow.com/questions/{random.randint(1000000, 9999999)}/{title.split()[2].lower()}-tutorial"
                ]
                
                url = random.choice(url_patterns)
                
                metadata = {
                    "url": url,
                    "title": title,
                    "meta_description": f"Learn {title.split()[3]} with {channel}",
                    "content_keywords": title.split()[:5],
                    "extracted_text": f"Educational content about {title.split()[3]}. " + 
                                     f"This tutorial covers fundamental concepts and practical applications.",
                    "domain": url.split('/')[2],
                    "has_video": "youtube.com" in url,
                    "has_forms": False,
                    "content_length": 2500
                }
                
                examples.append((metadata, mission, 1))  # 1 = productive
        
        # Create negative examples (entertainment/distracting content)
        self.logger.info("Generating negative examples (entertainment content)...")
        for i, mission in enumerate(missions[:100]):  # Same missions for comparison
            for _ in range(2):  # 2 distracting examples per mission
                channel = random.choice(entertainment_channels)
                
                # Create realistic entertainment URLs
                entertainment_urls = [
                    f"https://www.youtube.com/watch?v={self._generate_video_id()}",
                    f"https://www.reddit.com/r/memes/comments/{random.randint(100000, 999999)}/funny-cat-video",
                    f"https://www.instagram.com/p/{self._generate_video_id()[:11]}/",
                    f"https://www.tiktok.com/@{channel.lower().replace(' ', '')}",
                    f"https://www.twitch.tv/{channel.lower().replace(' ', '')}/videos"
                ]
                
                url = random.choice(entertainment_urls)
                
                # Entertainment titles
                entertainment_titles = [
                    f"Funny {random.choice(['Cat', 'Dog', 'Fails', 'Pranks'])} Compilation",
                    f"CRAZY {random.choice(['Gaming', 'Reactions', 'Challenges'])} Video!!!",
                    f"You Won't Believe What Happened...",
                    f"Epic {random.choice(['Dance', 'Music', 'Sports'])} Moments",
                    f"Ultimate {random.choice(['Memes', 'Vlogs', 'Drama'])} Collection"
                ]
                
                title = random.choice(entertainment_titles)
                
                metadata = {
                    "url": url,
                    "title": title,
                    "meta_description": f"Entertainment video from {channel}",
                    "content_keywords": title.split()[:3],
                    "extracted_text": f"Entertainment content. {title}. " +
                                     "Like and subscribe for more fun videos!",
                    "domain": url.split('/')[2],
                    "has_video": True,
                    "has_forms": False,
                    "content_length": 150
                }
                
                examples.append((metadata, mission, 0))  # 0 = distracting
        
        self.logger.info(f"Generated {len(examples)} training examples")
        return examples
    
    def _generate_video_id(self) -> str:
        """Generate a realistic YouTube video ID"""
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"
        return ''.join(random.choice(chars) for _ in range(11))
    
    def extract_features_from_examples(self, examples: List[Tuple[dict, str, int]]) -> Tuple[np.ndarray, np.ndarray]:
        """Extract features from training examples"""
        features_list = []
        labels_list = []
        
        self.logger.info("Extracting features from examples...")
        
        for i, (metadata, mission, label) in enumerate(examples):
            try:
                # Extract features using the same method as the main system
                features = self.feature_extractor.extract_features_from_metadata(metadata, mission)
                features_list.append(features)
                labels_list.append(label)
                
                if (i + 1) % 100 == 0:
                    self.logger.info(f"Processed {i + 1}/{len(examples)} examples")
                    
            except Exception as e:
                self.logger.warning(f"Error extracting features for example {i}: {e}")
                continue
        
        features_array = np.array(features_list)
        labels_array = np.array(labels_list)
        
        self.logger.info(f"Feature extraction complete: {features_array.shape[0]} examples, {features_array.shape[1]} features")
        return features_array, labels_array
    
    def load_existing_model(self) -> ProductivityClassifier:
        """Load existing trained model or create new one with correct dimensions"""
        model_path = os.path.join(os.path.dirname(__file__), "best_pretrained_model.pth")
        
        if os.path.exists(model_path):
            try:
                # Try to load the existing model state
                checkpoint = torch.load(model_path, map_location=self.device)
                
                # Check if the first layer weights match our expected input size
                expected_input_size = checkpoint['fc1.weight'].shape[1]
                
                if expected_input_size == self.input_size:
                    # Perfect match - load the existing model
                    model = ProductivityClassifier(self.input_size).to(self.device)
                    model.load_state_dict(checkpoint)
                    self.logger.info(f"✅ Loaded existing model from {model_path} ({expected_input_size} features)")
                    return model
                else:
                    # Size mismatch - use our new size but log the issue
                    self.logger.warning(f"⚠️ Model size mismatch: existing={expected_input_size}, current={self.input_size}")
                    self.logger.info("Creating new model with current feature dimensions")
                    model = ProductivityClassifier(self.input_size).to(self.device)
                    return model
                    
            except Exception as e:
                self.logger.warning(f"Error loading existing model: {e}")
                self.logger.info("Creating new model")
                model = ProductivityClassifier(self.input_size).to(self.device)
                return model
        else:
            self.logger.warning(f"No existing model found at {model_path}")
            self.logger.info("Creating new model")
            model = ProductivityClassifier(self.input_size).to(self.device)
            return model
    
    def train_incrementally(self, features: np.ndarray, labels: np.ndarray) -> ProductivityClassifier:
        """Train model incrementally with seed data"""
        # Convert to tensors
        features_tensor = torch.tensor(features, dtype=torch.float32)
        labels_tensor = torch.tensor(labels, dtype=torch.float32)
        
        # Split data for validation
        X_train, X_val, y_train, y_val = train_test_split(
            features_tensor, labels_tensor,
            test_size=0.2,
            random_state=42,
            stratify=labels_tensor
        )
        
        self.logger.info(f"Training set: {X_train.shape[0]} examples")
        self.logger.info(f"Validation set: {X_val.shape[0]} examples")
        
        # Load existing model
        model = self.load_existing_model()
        
        # Training setup with lower learning rate for incremental training
        optimizer = torch.optim.Adam(model.parameters(), lr=self.learning_rate, weight_decay=1e-5)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=2, gamma=0.8)
        loss_function = nn.BCELoss()
        
        best_val_accuracy = 0.0
        best_model_state = None
        
        self.logger.info(f"🔄 Starting incremental training for {self.epochs} epochs...")
        self.logger.info(f"📚 Adding seed data knowledge to existing model")
        
        for epoch in range(self.epochs):
            # Training phase
            model.train()
            total_loss = 0
            
            num_batches = len(X_train) // self.batch_size
            for i in range(0, len(X_train), self.batch_size):
                batch_features = X_train[i:i+self.batch_size]
                batch_labels = y_train[i:i+self.batch_size]
                
                # Forward pass
                predictions = model(batch_features)
                loss = loss_function(predictions.squeeze(), batch_labels)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / num_batches
            
            # Validation phase
            model.eval()
            with torch.no_grad():
                val_predictions = model(X_val)
                val_loss = loss_function(val_predictions.squeeze(), y_val)
                
                # Calculate accuracy
                predicted_labels = (val_predictions.squeeze() > 0.5).float()
                accuracy = (predicted_labels == y_val).float().mean()
            
            scheduler.step()
            
            self.logger.info(f"Epoch [{epoch+1}/{self.epochs}] - "
                           f"Train Loss: {avg_loss:.4f}, "
                           f"Val Loss: {val_loss:.4f}, "
                           f"Val Accuracy: {accuracy:.4f}")
            
            # Save best model
            if accuracy > best_val_accuracy:
                best_val_accuracy = accuracy
                best_model_state = model.state_dict().copy()
                self.logger.info(f"    ✨ New best accuracy: {accuracy:.4f}")
        
        # Restore best model state
        if best_model_state is not None:
            model.load_state_dict(best_model_state)
        
        return model, best_val_accuracy
    
    def save_updated_model(self, model: ProductivityClassifier, accuracy: float):
        """Save the incrementally trained model"""
        model_path = os.path.join(os.path.dirname(__file__), "best_pretrained_model.pth")
        backup_path = os.path.join(os.path.dirname(__file__), "previous_model_backup.pth")
        
        # Backup existing model first
        if os.path.exists(model_path):
            torch.save(torch.load(model_path), backup_path)
            self.logger.info(f"💾 Previous model backed up to {backup_path}")
        
        # Save updated model
        torch.save(model.state_dict(), model_path)
        
        self.logger.info(f"🚀 Updated model saved!")
        self.logger.info(f"📊 Final validation accuracy: {accuracy:.4f}")
        self.logger.info(f"💾 Saved to: {model_path}")
        
        if accuracy >= 0.85:
            self.logger.info("✅ High accuracy achieved! Model ready for deployment")
        else:
            self.logger.info("⚠️ Consider generating more training data for better performance")

def main():
    """Run incremental training with seed data"""
    print("🎯 Anchorite Incremental Training")
    print("🧠 Enhancing existing model with seed data knowledge")
    print("=" * 50)
    
    trainer = IncrementalTrainer()
    
    try:
        # Load seed data
        print("\n📂 Loading seed data...")
        seed_data = trainer.load_seed_data()
        
        # Generate training examples
        print("\n🏗️ Generating training examples...")
        examples = trainer.generate_training_examples(seed_data)
        
        # Extract features
        print("\n🔍 Extracting features...")
        features, labels = trainer.extract_features_from_examples(examples)
        
        # Train incrementally
        print("\n🎓 Training model incrementally...")
        model, accuracy = trainer.train_incrementally(features, labels)
        
        # Save updated model
        print("\n💾 Saving updated model...")
        trainer.save_updated_model(model, accuracy)
        
        print("\n🎉 Incremental training completed successfully!")
        print(f"📈 Model enhanced with {len(examples)} new examples")
        print(f"🎯 Final accuracy: {accuracy:.2%}")
        
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        logging.error(f"Training failed: {e}")
        raise

if __name__ == "__main__":
    main()
