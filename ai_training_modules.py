"""
AI Training Infrastructure for Backend Generation
Supports training models to generate backends from frontend analysis
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import transformers
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForCausalLM,
    TrainingArguments, Trainer, pipeline
)
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import json
import pickle
import logging
from typing import Dict, List, Tuple, Any, Optional
import os
from dataclasses import dataclass
import wandb  # For experiment tracking
from config import AIConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainingConfig:
    """Configuration for AI model training"""
    model_name: str = AIConfig.MODEL_NAME
    max_length: int = AIConfig.MAX_LENGTH
    batch_size: int = AIConfig.BATCH_SIZE
    learning_rate: float = AIConfig.LEARNING_RATE
    num_epochs: int = AIConfig.NUM_EPOCHS
    warmup_steps: int = 500
    logging_steps: int = 100
    save_steps: int = 1000
    output_dir: str = AIConfig.MODEL_OUTPUT_DIR
    use_wandb: bool = AIConfig.USE_WANDB
    gradient_accumulation_steps: int = 4

class FrontendBackendDataset(Dataset):
    """Dataset for frontend-to-backend mapping training"""
    
    def __init__(self, data: List[Dict], tokenizer, max_length: int = 512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Combine frontend analysis with backend requirements
        input_text = f"Frontend: {item['frontend_analysis']} Requirements: {item['requirements']}"
        target_text = item['backend_code']
        
        # Tokenize input and target
        input_encoding = self.tokenizer(
            input_text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        target_encoding = self.tokenizer(
            target_text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': input_encoding['input_ids'].flatten(),
            'attention_mask': input_encoding['attention_mask'].flatten(),
            'labels': target_encoding['input_ids'].flatten()
        }

class BackendGeneratorModel(nn.Module):
    """Neural network model for generating backend code"""
    
    def __init__(self, model_name: str = AIConfig.MODEL_NAME):
        super().__init__()
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Add special tokens for our use case
        special_tokens = {
            "pad_token": "<pad>",
            "additional_special_tokens": [
                "<frontend>", "</frontend>",
                "<backend>", "</backend>",
                "<api>", "</api>",
                "<database>", "</database>",
                "<auth>", "</auth>"
            ]
        }
        self.tokenizer.add_special_tokens(special_tokens)
        self.model.resize_token_embeddings(len(self.tokenizer))
    
    def forward(self, input_ids, attention_mask, labels=None):
        return self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )

class AITrainer:
    """Main trainer class for backend generation AI"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.trainer = None
        
        # Initialize wandb if enabled
        if config.use_wandb:
            wandb.init(project=AIConfig.WANDB_PROJECT, config=config.__dict__)
    
    def load_model(self):
        """Load and initialize the model"""
        logger.info(f"Loading model: {self.config.model_name}")
        self.model = BackendGeneratorModel(self.config.model_name)
        self.tokenizer = self.model.tokenizer
    
    def prepare_dataset(self, data_path: str) -> Tuple[Dataset, Dataset]:
        """Prepare training and validation datasets"""
        logger.info(f"Loading dataset from: {data_path}")
        
        # Load your dataset (JSON, CSV, etc.)
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        # Split into train/validation
        train_data, val_data = train_test_split(data, test_size=0.2, random_state=42)
        
        train_dataset = FrontendBackendDataset(train_data, self.tokenizer, self.config.max_length)
        val_dataset = FrontendBackendDataset(val_data, self.tokenizer, self.config.max_length)
        
        return train_dataset, val_dataset
    
    def train(self, train_dataset: Dataset, val_dataset: Dataset):
        """Train the model"""
        logger.info("Starting training...")
        
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            per_device_eval_batch_size=self.config.batch_size,
            warmup_steps=self.config.warmup_steps,
            weight_decay=0.01,
            logging_dir='./logs',
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            evaluation_strategy="steps",
            eval_steps=self.config.save_steps,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            report_to="wandb" if self.config.use_wandb else None,
        )
        
        self.trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.tokenizer,
        )
        
        # Start training
        self.trainer.train()
        
        # Save the final model
        self.trainer.save_model()
        self.tokenizer.save_pretrained(self.config.output_dir)
        
        logger.info("Training completed!")
    
    def save_model(self, path: str):
        """Save the trained model"""
        if self.model:
            self.model.model.save_pretrained(path)
            self.tokenizer.save_pretrained(path)
            logger.info(f"Model saved to: {path}")

# Main training pipeline
def main():
    """Main training pipeline"""
    config = TrainingConfig()
    trainer = AITrainer(config)
    
    # Load model
    trainer.load_model()
    
    # Prepare dataset (you'll provide this)
    train_dataset, val_dataset = trainer.prepare_dataset(AIConfig.TRAINING_DATA_PATH)
    
    # Train the model
    trainer.train(train_dataset, val_dataset)
    
    # Save the trained model
    trainer.save_model('./trained_backend_generator')

if __name__ == "__main__":
    main()
