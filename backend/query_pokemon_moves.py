#!/usr/bin/env python3
"""
Query Pokemon Moves from the database
This script helps you find moves for specific Pokemon by ID and level.
"""

import sqlite3
import sys
from typing import List, Tuple, Optional

def connect_db(db_path: str = "pokemon.db") -> sqlite3.Connection:
    """Connect to the Pokemon database."""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # This allows us to access columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def get_pokemon_moves(conn: sqlite3.Connection, pokemon_id: int, max_level: Optional[int] = None) -> List[Tuple]:
    """
    Get all moves for a specific Pokemon ID.
    
    Args:
        conn: Database connection
        pokemon_id: The ID of the Pokemon (1=Bulbasaur, 25=Pikachu, etc.)
        max_level: Optional maximum level to filter moves (only shows moves learnable at this level or below)
    
    Returns:
        List of tuples: (move_id, move_name, level_learned, move_type, power, accuracy, pp)
    """
    query = """
    SELECT 
        pm.move_id,
        m.name as move_name,
        pm.level_learned,
        m.type as move_type,
        m.power,
        m.accuracy,
        m.pp
    FROM PokemonMoves pm
    JOIN Moves m ON pm.move_id = m.id
    WHERE pm.pokemon_id = ?
    """
    
    params = [pokemon_id]
    
    if max_level is not None:
        query += " AND (pm.level_learned <= ? OR pm.level_learned = 0)"
        params.append(max_level)
    
    query += " ORDER BY pm.level_learned, m.name"
    
    cursor = conn.execute(query, params)
    return cursor.fetchall()

def get_moves_by_level(conn: sqlite3.Connection, pokemon_id: int, level: int) -> List[Tuple]:
    """
    Get moves that a Pokemon learns exactly at a specific level.
    
    Args:
        conn: Database connection
        pokemon_id: The ID of the Pokemon
        level: The exact level to check
    
    Returns:
        List of moves learned at that specific level
    """
    query = """
    SELECT 
        pm.move_id,
        m.name as move_name,
        pm.level_learned,
        m.type as move_type,
        m.power,
        m.accuracy,
        m.pp
    FROM PokemonMoves pm
    JOIN Moves m ON pm.move_id = m.id
    WHERE pm.pokemon_id = ? AND pm.level_learned = ?
    ORDER BY m.name
    """
    
    cursor = conn.execute(query, [pokemon_id, level])
    return cursor.fetchall()

def get_tm_hm_moves(conn: sqlite3.Connection, pokemon_id: int) -> List[Tuple]:
    """
    Get all TM/HM moves (level_learned = 0) for a Pokemon.
    
    Args:
        conn: Database connection
        pokemon_id: The ID of the Pokemon
    
    Returns:
        List of TM/HM moves
    """
    query = """
    SELECT 
        pm.move_id,
        m.name as move_name,
        pm.level_learned,
        m.type as move_type,
        m.power,
        m.accuracy,
        m.pp
    FROM PokemonMoves pm
    JOIN Moves m ON pm.move_id = m.id
    WHERE pm.pokemon_id = ? AND pm.level_learned = 0
    ORDER BY m.name
    """
    
    cursor = conn.execute(query, [pokemon_id])
    return cursor.fetchall()

def get_level_up_moves(conn: sqlite3.Connection, pokemon_id: int) -> List[Tuple]:
    """
    Get all level-up moves (level_learned > 0) for a Pokemon.
    
    Args:
        conn: Database connection
        pokemon_id: The ID of the Pokemon
    
    Returns:
        List of level-up moves
    """
    query = """
    SELECT 
        pm.move_id,
        m.name as move_name,
        pm.level_learned,
        m.type as move_type,
        m.power,
        m.accuracy,
        m.pp
    FROM PokemonMoves pm
    JOIN Moves m ON pm.move_id = m.id
    WHERE pm.pokemon_id = ? AND pm.level_learned > 0
    ORDER BY pm.level_learned, m.name
    """
    
    cursor = conn.execute(query, [pokemon_id])
    return cursor.fetchall()

def print_moves(moves: List[Tuple], title: str):
    """Pretty print a list of moves."""
    print(f"\n{title}")
    print("=" * len(title))
    
    if not moves:
        print("No moves found.")
        return
    
    print(f"{'Move ID':<8} {'Move Name':<20} {'Level':<6} {'Type':<10} {'Power':<6} {'Acc':<4} {'PP':<3}")
    print("-" * 70)
    
    for move in moves:
        move_id, name, level, move_type, power, accuracy, pp = move
        level_str = str(level) if level > 0 else "TM/HM"
        power_str = str(power) if power else "-"
        acc_str = str(accuracy) if accuracy else "-"
        
        print(f"{move_id:<8} {name:<20} {level_str:<6} {move_type:<10} {power_str:<6} {acc_str:<4} {pp:<3}")

def get_pokemon_name(conn: sqlite3.Connection, pokemon_id: int) -> str:
    """Get the name of a Pokemon by ID."""
    cursor = conn.execute("SELECT name FROM Pokemon WHERE id = ?", [pokemon_id])
    result = cursor.fetchone()
    return result[0] if result else f"Pokemon #{pokemon_id}"

def main():
    """Main function to demonstrate usage."""
    if len(sys.argv) < 2:
        print("Usage: python query_pokemon_moves.py <pokemon_id> [max_level]")
        print("Example: python query_pokemon_moves.py 25 10  # Pikachu moves up to level 10")
        print("Example: python query_pokemon_moves.py 1      # All Bulbasaur moves")
        sys.exit(1)
    
    pokemon_id = int(sys.argv[1])
    max_level = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    conn = connect_db()
    
    try:
        pokemon_name = get_pokemon_name(conn, pokemon_id)
        print(f"Moves for {pokemon_name} (ID: {pokemon_id})")
        
        if max_level:
            print(f"Showing moves available up to level {max_level}")
            all_moves = get_pokemon_moves(conn, pokemon_id, max_level)
            print_moves(all_moves, f"All Available Moves (up to level {max_level})")
        else:
            # Show level-up moves
            level_moves = get_level_up_moves(conn, pokemon_id)
            print_moves(level_moves, "Level-up Moves")
            
            # Show TM/HM moves
            tm_moves = get_tm_hm_moves(conn, pokemon_id)
            print_moves(tm_moves, "TM/HM Moves")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
