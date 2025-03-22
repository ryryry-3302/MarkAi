"""
Main application file for the Marketing Analytics Backend.
This file initializes the Flask application and registers all routes.
"""
from flask import Flask
from api.routes import register_routes
from config.settings import Config
from database.supabase_client import initialize_supabase

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Supabase client
    initialize_supabase()
    
    # Register blueprints/routes
    register_routes(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
