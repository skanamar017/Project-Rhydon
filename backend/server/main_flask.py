"""
Flask application factory for Pokemon Team Management API.
Registers blueprints and handles application setup.
"""

from flask import Flask, jsonify
from flask_cors import CORS
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
# Add battle_routes import
from routes.battle_routes import battle_routes

def create_app():
    from flask import request

    def home():
        return {"message": "Pokemon Team API"}

    def receive_message():
        data = request.json
        print("Received from other server:", data)
        return jsonify({"status": "received", "echo": data})

    def send_to_other_server():
        import requests
        # You can change this port to the other instance's port (e.g., 5000 or 5001)
        other_server_url = request.json.get('url', 'http://localhost:5000/receive_message')
        payload = request.json.get('payload', {"message": "Hello from this server!"})
        try:
            response = requests.post(other_server_url, json=payload, timeout=3)
            return jsonify({"response_from_other": response.json()})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    app = Flask(__name__)

    # Configure CORS
    CORS(app)

    # Register blueprints with URL prefixes
    app.register_blueprint(team_bp, url_prefix='/Teams')
    app.register_blueprint(pokemon_bp, url_prefix='/Teams')
    app.register_blueprint(move_bp)
    # Register battle sim routes (no prefix for simplicity)
    app.register_blueprint(battle_routes)

    # Register all routes using add_url_rule
    app.add_url_rule('/', view_func=home, methods=['GET'])
    app.add_url_rule('/receive_message', view_func=receive_message, methods=['POST'])
    app.add_url_rule('/send_to_other_server', view_func=send_to_other_server, methods=['POST'])

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
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'legacy', 'setup_evolution_system.py'))
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
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'legacy', 'setup_evolution_system.py'))
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
            script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'legacy', 'setup_evolution_system.py'))
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
