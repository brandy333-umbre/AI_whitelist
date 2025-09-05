#!/usr/bin/env python3
"""
Enhanced Training Script for LLM-Generated Data
Uses the enhanced metadata format for 90% accuracy MVP training
"""

import numpy as np
import torch
import torch.nn as nn
import logging
import json
import os
from typing import List, Tuple
from sklearn.model_selection import train_test_split
from rl_filter import URLFeatureExtractor, ProductivityClassifier


class EnhancedDataTrainer:
    """Trainer for enhanced data with pre-generated metadata"""
    
    def __init__(self):
        self.feature_extractor = URLFeatureExtractor()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Enhanced model parameters
        self.input_size = 1187  # Enhanced feature size
        self.epochs = 20
        self.batch_size = 64
        self.learning_rate = 0.001
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_enhanced_training_data(self, data_file: str = "enhanced_training_data.json"):
        """Load LLM-generated enhanced training data"""
        data_path = os.path.join(os.path.dirname(__file__), data_file)
        
        with open(data_path, "r", encoding='utf-8') as f:
            training_data = json.load(f)
        
        print(f"Loaded {len(training_data['examples'])} enhanced training examples")
        
        all_features = []
        all_labels = []
        
        # Process examples with pre-generated enhanced metadata
        for i, example in enumerate(training_data['examples']):
            if i % 1000 == 0:
                print(f"Processing example {i}/{len(training_data['examples'])}")
            
            try:
                # Use the pre-generated enhanced metadata directly
                enhanced_metadata = example['enhanced_metadata']
                
                # Create metadata in the format expected by feature extractor
                metadata = {
                    "url": example["url"],
                    "title": enhanced_metadata.get("title", ""),
                    "meta_description": enhanced_metadata.get("meta_description", ""),
                    "content_keywords": enhanced_metadata.get("content_keywords", []),
                    "extracted_text": enhanced_metadata.get("extracted_text", ""),
                    "domain": enhanced_metadata.get("domain", ""),
                    "path": enhanced_metadata.get("path", ""),
                    "query_params": enhanced_metadata.get("query_params", {}),
                    "has_video": enhanced_metadata.get("has_video", False),
                    "has_forms": enhanced_metadata.get("has_forms", False),
                    "content_length": enhanced_metadata.get("content_length", 0),
                    "images_count": enhanced_metadata.get("images_count", 0),
                    "links_count": enhanced_metadata.get("links_count", 0),
                    "external_links_count": enhanced_metadata.get("external_links_count", 0),
                    "response_time_ms": enhanced_metadata.get("response_time_ms", 0),
                    
                    # Enhanced YouTube features
                    "youtube_title": enhanced_metadata.get("youtube_title", ""),
                    "youtube_description": enhanced_metadata.get("youtube_description", ""),
                    "youtube_channel": enhanced_metadata.get("youtube_channel", ""),
                    "youtube_category": enhanced_metadata.get("youtube_category", ""),
                    "content_quality_score": enhanced_metadata.get("content_quality_score", 0.0),
                    "educational_indicators": enhanced_metadata.get("educational_indicators", 0),
                    "entertainment_indicators": enhanced_metadata.get("entertainment_indicators", 0),
                    
                    # Open Graph data
                    "og_title": enhanced_metadata.get("og_title", ""),
                    "og_description": enhanced_metadata.get("og_description", ""),
                    "og_type": enhanced_metadata.get("og_type", ""),
                    
                    # Content analysis
                    "paragraph_count": enhanced_metadata.get("paragraph_count", 0),
                    "heading_count": enhanced_metadata.get("heading_count", 0),
                    "list_count": enhanced_metadata.get("list_count", 0),
                    "avg_paragraph_length": enhanced_metadata.get("avg_paragraph_length", 0),
                    "has_structured_content": enhanced_metadata.get("has_structured_content", False),
                    "has_code": enhanced_metadata.get("has_code", False),
                    "code_block_count": enhanced_metadata.get("code_block_count", 0)
                }
                
                # Extract features using enhanced metadata
                features = self.feature_extractor.extract_features_from_metadata(
                    metadata, example['mission']
                )
                
                all_features.append(features)
                all_labels.append(example['label'])
                
            except Exception as e:
                self.logger.warning(f"Failed to process example {i}: {e}")
                continue
        
        print(f"Successfully processed {len(all_features)} examples")
        print(f"Feature vector size: {all_features[0].shape}")
        print(f"Labels: {np.sum(all_labels)} productive, {len(all_labels) - np.sum(all_labels)} distracting")
        
        return np.array(all_features), np.array(all_labels)
    
    def create_model(self):
        """Create enhanced productivity classifier"""
        model = ProductivityClassifier(self.input_size).to(self.device)
        return model
    
    def train_model(self, features, labels):
        """Train the enhanced model for MVP deployment"""
        # Convert to tensors
        features_tensor = torch.tensor(features, dtype=torch.float32)
        labels_tensor = torch.tensor(labels, dtype=torch.float32)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features_tensor, labels_tensor,
            test_size=0.15,  # Smaller test set for more training data
            random_state=42,
            stratify=labels_tensor
        )
        
        print(f"Training set: {X_train.shape[0]} examples")
        print(f"Testing set: {X_test.shape[0]} examples")
        
        # Create model
        model = self.create_model()
        
        # Training setup - optimized for high accuracy
        optimizer = torch.optim.Adam(model.parameters(), lr=self.learning_rate, weight_decay=1e-5)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.5)
        loss_function = nn.BCELoss()
        
        # Track best model
        best_test_accuracy = 0.0
        best_model_state = None
        
        print(f"🚀 Training enhanced model for {self.epochs} epochs...")
        print("🎯 Target: 90%+ accuracy for MVP deployment")
        
        # Training loop
        for epoch in range(self.epochs):
            model.train()
            total_loss = 0
            
            # Process in batches
            num_batches = len(X_train) // self.batch_size
            for batch_idx, i in enumerate(range(0, len(X_train), self.batch_size)):
                batch_features = X_train[i:i+self.batch_size].to(self.device)
                batch_labels = y_train[i:i+self.batch_size].to(self.device)
                
                # Forward pass
                predictions = model(batch_features)
                loss = loss_function(predictions.squeeze(), batch_labels)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
                
                # Progress updates
                if (batch_idx + 1) % 100 == 0:
                    print(f"    Batch {batch_idx + 1}/{num_batches}, Loss: {loss.item():.4f}")
            
            # Step scheduler
            scheduler.step()
            
            avg_loss = total_loss / num_batches
            
            # Evaluate on test set
            model.eval()
            with torch.no_grad():
                X_test_device = X_test.to(self.device)
                y_test_device = y_test.to(self.device)
                
                test_predictions = model(X_test_device)
                test_loss = loss_function(test_predictions.squeeze(), y_test_device)
                
                # Calculate accuracy
                predicted_labels = (test_predictions.squeeze() > 0.5).float()
                accuracy = (predicted_labels == y_test_device).float().mean()
            
            print(f"Epoch [{epoch+1}/{self.epochs}], Train Loss: {avg_loss:.4f}, Test Loss: {test_loss:.4f}, Test Accuracy: {accuracy:.4f}")
            
            # Save best model based on accuracy
            if accuracy > best_test_accuracy:
                best_test_accuracy = accuracy
                best_model_state = model.state_dict().copy()
                print(f"    → 🎯 New best accuracy! {accuracy:.4f}")
                
                # Check if we hit MVP target
                if accuracy >= 0.90:
                    print(f"    🎉 MVP TARGET ACHIEVED! 90%+ accuracy reached")
        
        # Save MVP model
        if best_model_state is not None:
            mvp_model_path = os.path.join(os.path.dirname(__file__), "mvp_enhanced_model.pth")
            torch.save(best_model_state, mvp_model_path)
            
            # Replace the main model for deployment
            main_model_path = os.path.join(os.path.dirname(__file__), "best_pretrained_model.pth") 
            torch.save(best_model_state, main_model_path)
            
            print(f"\n🚀 MVP MODEL READY FOR DEPLOYMENT!")
            print(f"📊 Final Accuracy: {best_test_accuracy:.4f}")
            print(f"💾 Saved to: {main_model_path}")
            
            if best_test_accuracy >= 0.90:
                print(f"✅ SHIP IT! Model exceeds 90% accuracy target")
            else:
                print(f"⚠️ WARNING: Model accuracy {best_test_accuracy:.1%} below 90% target")
                print(f"Consider: More training data, different hyperparameters, or feature engineering")
        
        return model, best_test_accuracy


def main():
    """Train enhanced model with LLM-generated data"""
    print("🧠 Training Enhanced Model with LLM-Generated Data...")
    print("🎯 Target: 90% accuracy for MVP deployment")
    
    trainer = EnhancedDataTrainer()
    
    # Load LLM-generated enhanced training data
    features, labels = trainer.load_enhanced_training_data("enhanced_training_data.json")
    
    # Train MVP model
    model, accuracy = trainer.train_model(features, labels)
    
    print(f"\n🎉 Training Complete!")
    print(f"📈 Final Accuracy: {accuracy:.4f}")
    
    if accuracy >= 0.90:
        print(f"🚀 READY TO SHIP! Model meets MVP requirements")
    else:
        print(f"📋 Need more data or tuning to reach 90% target")


if __name__ == "__main__":
    main()
