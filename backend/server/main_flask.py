"""
Flask application factory for Pokemon Team Management API.
Registers blueprints and handles application setup.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
import sqlite3
import subprocess
import sys
import os

# Add the parent directory to sys.path to import from backend/
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import blueprints - they'll need to be updated to use backend/ imports
from routes.team_routes import team_bp
from routes.pokemon_routes import pokemon_bp
from routes.move_routes import move_bp
from routes.user_routes import user_bp
from server.user_model import User
from database.services.database_service import PokemonDatabase

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.secret_key = 'super-secret-key'  # Change this in production!

    # Configure CORS
    CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5001", "null"])
    CORS(team_bp, supports_credentials=True, origins=["http://127.0.0.1:5001", "null"])
    CORS(pokemon_bp, supports_credentials=True, origins=["http://127.0.0.1:5001", "null"])
    CORS(move_bp, supports_credentials=True, origins=["http://127.0.0.1:5001", "null"])
    from routes.user_routes import user_bp
    CORS(user_bp, supports_credentials=True, origins=["http://127.0.0.1:5001", "null"])

    # Set up flask-login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = None  # Disable redirect for API

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({'error': 'Unauthorized'}), 401

    @login_manager.user_loader
    def load_user(user_id):
        db = PokemonDatabase()
        # Find account by id
        conn = sqlite3.connect(db.db_path)
        cursor = conn.execute("SELECT id, username, password_hash FROM Account WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(id=row[0], username=row[1], password_hash=row[2])
        return None

    # Register blueprints with URL prefixes
    app.register_blueprint(team_bp, url_prefix='/Teams')
    app.register_blueprint(pokemon_bp, url_prefix='/Teams')
    app.register_blueprint(move_bp)
    app.register_blueprint(user_bp, url_prefix='/user')

    # Home route
    @app.route("/", methods=["GET"])
    def home():
        return {"message": "Pokemon Team API"}
    
    return app

# Create the app instance
app = create_app()

def setup_evolution_system():
    """Automatically set up the evolution system if it doesn't exist"""
    try:
        print("🔍 Checking evolution system status...")
        
        # Use the database service to get the correct database path
        from database.services.database_service import PokemonDatabase
        db = PokemonDatabase()
        
        # Check if Evolution table exists and has data
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Check if Evolution table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='Evolution'
        """)
        
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("❌ Evolution table not found")
            print("🚀 Setting up evolution system automatically...")
            conn.close()
            
            # Run the external setup script from the legacy directory
            script_path = os.path.join("..", "database", "legacy", "setup_evolution_system.py")
            result = subprocess.run(["python", script_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Evolution system setup completed!")
            else:
                print(f"❌ Setup failed: {result.stderr}")
            return True
        
        # Check if table has data
        cursor.execute("SELECT COUNT(*) FROM Evolution")
        evolution_count = cursor.fetchone()[0]
        
        if evolution_count == 0:
            print("❌ Evolution table is empty")
            print("🚀 Setting up evolution system automatically...")
            conn.close()
            
            # Run the external setup script from the legacy directory
            script_path = os.path.join("..", "database", "legacy", "setup_evolution_system.py")
            result = subprocess.run(["python", script_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Evolution system setup completed!")
            else:
                print(f"❌ Setup failed: {result.stderr}")
            return True
        
        # Check if PokemonMoves has evolution moves (rough estimate)
        cursor.execute("SELECT COUNT(*) FROM PokemonMoves")
        total_moves = cursor.fetchone()[0]
        
        conn.close()
        
        if total_moves < 4100:  # Should be around 4172 with evolution moves
            print(f"⚠️  PokemonMoves count ({total_moves}) suggests missing evolution moves")
            print("🚀 Updating Pokemon moves with evolution data...")
            
            # Run the external setup script from the legacy directory
            script_path = os.path.join("..", "database", "legacy", "setup_evolution_system.py")
            result = subprocess.run(["python", script_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Evolution system setup completed!")
            else:
                print(f"❌ Setup failed: {result.stderr}")
            return True
        
        print(f"✅ Evolution system already set up ({evolution_count} evolutions, {total_moves} moves)")
        return False
        
    except Exception as e:
        print(f"❌ Error checking evolution system: {e}")
        return False

if __name__ == "__main__":
    # Automatically set up evolution system on startup
    setup_evolution_system()
    app.run(debug=True, port=5001)
