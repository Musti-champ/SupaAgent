import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the AI-enhanced scraper."""
    
    # Venice AI OpenRouter settings
    VENICE_API_KEY = os.getenv('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')
    OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    
    # Scraping settings
    DEFAULT_DELAY = float(os.getenv('SCRAPING_DELAY', '1.0'))
    MAX_DEPTH = int(os.getenv('MAX_CRAWL_DEPTH', '3'))
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # AI Analysis settings
    AI_ANALYSIS_ENABLED = os.getenv('AI_ANALYSIS_ENABLED', 'true').lower() == 'true'
    CONTENT_TRANSFORMATION_ENABLED = os.getenv('CONTENT_TRANSFORMATION_ENABLED', 'true').lower() == 'true'
    URL_PRIORITIZATION_ENABLED = os.getenv('URL_PRIORITIZATION_ENABLED', 'true').lower() == 'true'
    
    # Rate limiting
    REQUESTS_PER_MINUTE = int(os.getenv('REQUESTS_PER_MINUTE', '30'))
    
    # AI training and backend generation configuration
    MODEL_NAME = os.getenv('SupaAi','miles', 'microsoft/DialoGPT-medium')
    MAX_LENGTH = int(os.getenv('AI_MAX_LENGTH', '512'))
    BATCH_SIZE = int(os.getenv('AI_BATCH_SIZE', '8'))
    LEARNING_RATE = float(os.getenv('AI_LEARNING_RATE', '5e-5'))
    NUM_EPOCHS = int(os.getenv('AI_NUM_EPOCHS', '3'))
    
    DEFAULT_BACKEND_FRAMEWORK = os.getenv('DEFAULT_BACKEND_FRAMEWORK', 'fastapi')
    DEFAULT_DATABASE = os.getenv('DEFAULT_DATABASE', 'postgresql')
    
    TRAINING_DATA_PATH = os.getenv('TRAINING_DATA_PATH', './datasets/training_data.json')
    MODEL_OUTPUT_DIR = os.getenv('MODEL_OUTPUT_DIR', './models')
    
    WANDB_PROJECT = os.getenv('WANDB_PROJECT', 'backend-generator')
    USE_WANDB = os.getenv('USE_WANDB', 'true').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.VENICE_API_KEY:
            raise ValueError("VENICE_API_KEY environment variable is required")
        
        return True
