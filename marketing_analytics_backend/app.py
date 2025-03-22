"""
Main application file for the Marketing Analytics Backend.
This file initializes the Flask application and registers all routes.
"""
from flask import Flask
from api.routes import register_routes
from config.settings import Config
from database.models import db

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints/routes
    register_routes(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
