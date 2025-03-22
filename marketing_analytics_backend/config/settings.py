"""
Configuration settings for the Marketing Analytics Backend.
Loads environment variables and provides configuration for the application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/marketing_analytics')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API credentials
    INSTAGRAM_API_KEY = os.getenv('INSTAGRAM_API_KEY')
    INSTAGRAM_API_SECRET = os.getenv('INSTAGRAM_API_SECRET')
    
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    TIKTOK_API_KEY = os.getenv('TIKTOK_API_KEY')
    TIKTOK_API_SECRET = os.getenv('TIKTOK_API_SECRET')
    
    # Google Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Scheduler settings
    SCHEDULER_API_ENABLED = True
    JOBS = [
        {
            'id': 'fetch_instagram_data',
            'func': 'data_ingestion.tasks:fetch_instagram_data',
            'trigger': 'interval',
            'hours': 6
        },
        {
            'id': 'fetch_youtube_data',
            'func': 'data_ingestion.tasks:fetch_youtube_data',
            'trigger': 'interval',
            'hours': 6
        },
        {
            'id': 'fetch_tiktok_data',
            'func': 'data_ingestion.tasks:fetch_tiktok_data',
            'trigger': 'interval',
            'hours': 6
        },
        {
            'id': 'run_analytics',
            'func': 'analytics.tasks:run_analytics',
            'trigger': 'cron',
            'hour': 1  # Run at 1 AM daily
        }
    ]
