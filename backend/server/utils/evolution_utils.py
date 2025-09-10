"""
Evolution system utilities for automatic setup on Flask app startup.
"""

import sqlite3
import subprocess
import os

def setup_evolution_system():
    """Automatically set up the evolution system if it doesn't exist"""
    try:
        print("🔍 Checking evolution system status...")
        
        # Check if database exists
        if not os.path.exists("pokemon.db"):
            print("❌ Pokemon database not found")
            return False
        
        # Check if Evolution table exists and has data
        conn = sqlite3.connect("pokemon.db")
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
            
            # Run the external setup script
            result = subprocess.run(["python", "setup_evolution_system.py"], 
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
            
            # Run the external setup script
            result = subprocess.run(["python", "setup_evolution_system.py"], 
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
            
            # Run the external setup script
            result = subprocess.run(["python", "setup_evolution_system.py"], 
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
