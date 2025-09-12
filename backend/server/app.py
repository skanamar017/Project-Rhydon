"""
Simplified and modular Flask application for Pokemon team management.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from flask_cors import CORS
from routes.team_routes import team_bp
from routes.pokemon_routes import pokemon_bp
from routes.move_routes import move_bp
from routes.auth_routes import auth_bp
from utils.evolution_utils import setup_evolution_system

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(team_bp, url_prefix='/Teams')
    app.register_blueprint(pokemon_bp, url_prefix='/Teams')
    app.register_blueprint(move_bp, url_prefix='/')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    @app.route("/", methods=["GET"])
    def home():
        return {"message": "Pokemon Team API"}
    
    return app

if __name__ == "__main__":
    # Automatically set up evolution system on startup
    setup_evolution_system()
    
    # Create and run the app
    app = create_app()
    app.run(debug=True, port=5001)
