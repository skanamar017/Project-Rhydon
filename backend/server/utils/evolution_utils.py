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
            print("❌ Evolution table not found. Please run the database setup script to initialize evolution data.")
            conn.close()
            return True
        
        # Check if table has data
        cursor.execute("SELECT COUNT(*) FROM Evolution")
        evolution_count = cursor.fetchone()[0]
        
        if evolution_count == 0:
            print("❌ Evolution table is empty. Please run the database setup script to initialize evolution data.")
            conn.close()
            return True
        
        # Check if PokemonMoves has evolution moves (rough estimate)
        cursor.execute("SELECT COUNT(*) FROM PokemonMoves")
        total_moves = cursor.fetchone()[0]
        
        conn.close()
        
        if total_moves < 4100:  # Should be around 4172 with evolution moves
            print(f"⚠️  PokemonMoves count ({total_moves}) suggests missing evolution moves.")
            print("Please run the database setup script to update evolution moves.")
            return True
        
        print(f"✅ Evolution system already set up ({evolution_count} evolutions, {total_moves} moves)")
        return False
        
    except Exception as e:
        print(f"❌ Error checking evolution system: {e}")
        return False
