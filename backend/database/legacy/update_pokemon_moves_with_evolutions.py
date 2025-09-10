#!/usr/bin/env python3
"""
Update PokemonMoves table to include moves learned from previous evolutions.
This ensures that evolved Pokemon know all moves they could have learned
in their pre-evolution forms.
"""

import sqlite3
from typing import List, Dict, Set

def get_evolution_chain(cursor, pokemon_id: int) -> List[int]:
    """Get the full evolution chain leading to a Pokemon (including itself)"""
    chain = []
    
    # Recursively find all pre-evolutions
    def find_pre_evolutions(current_id: int, visited: Set[int]):
        if current_id in visited:
            return  # Prevent infinite loops
        visited.add(current_id)
        
        # Find what this Pokemon evolves from
        cursor.execute("""
            SELECT from_pokemon_id FROM Evolution 
            WHERE to_pokemon_id = ?
        """, (current_id,))
        
        pre_evolutions = cursor.fetchall()
        for (pre_evo_id,) in pre_evolutions:
            find_pre_evolutions(pre_evo_id, visited)
            if pre_evo_id not in chain:
                chain.append(pre_evo_id)
        
        if current_id not in chain:
            chain.append(current_id)
    
    find_pre_evolutions(pokemon_id, set())
    return chain

def main():
    # Connect to database
    conn = sqlite3.connect('pokemon.db')
    cursor = conn.cursor()
    
    print("Updating PokemonMoves table to include moves from previous evolutions...")
    
    # Get all Pokemon
    cursor.execute("SELECT pokedex_number FROM Pokemon ORDER BY pokedex_number")
    all_pokemon = [row[0] for row in cursor.fetchall()]
    
    moves_added = 0
    
    for pokemon_id in all_pokemon:
        print(f"Processing Pokemon #{pokemon_id}...")
        
        # Get evolution chain (all pre-evolutions and current Pokemon)
        evolution_chain = get_evolution_chain(cursor, pokemon_id)
        
        if len(evolution_chain) <= 1:
            continue  # No pre-evolutions, skip
        
        # Get all moves this Pokemon can currently learn
        cursor.execute("""
            SELECT move_id, level_learned FROM PokemonMoves 
            WHERE pokemon_id = ?
        """, (pokemon_id,))
        current_moves = {row[0]: row[1] for row in cursor.fetchall()}
        
        # For each pre-evolution, get their moves
        for pre_evo_id in evolution_chain[:-1]:  # Exclude the current Pokemon itself
            cursor.execute("""
                SELECT move_id, level_learned FROM PokemonMoves 
                WHERE pokemon_id = ?
            """, (pre_evo_id,))
            
            pre_evo_moves = cursor.fetchall()
            
            for move_id, level_learned in pre_evo_moves:
                # Skip if the current Pokemon already knows this move
                if move_id in current_moves:
                    continue
                
                # Check if this move exists in the Moves table
                cursor.execute("SELECT id FROM Moves WHERE id = ?", (move_id,))
                if not cursor.fetchone():
                    continue
                
                # Add the move to the current Pokemon's moveset
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO PokemonMoves (pokemon_id, move_id, level_learned)
                        VALUES (?, ?, ?)
                    """, (pokemon_id, move_id, level_learned))
                    
                    if cursor.rowcount > 0:
                        moves_added += 1
                        
                        # Get move and pre-evolution names for logging
                        cursor.execute("SELECT name FROM Moves WHERE id = ?", (move_id,))
                        move_name = cursor.fetchone()[0]
                        
                        cursor.execute("SELECT name FROM Pokemon WHERE pokedex_number = ?", (pre_evo_id,))
                        pre_evo_name = cursor.fetchone()[0]
                        
                        cursor.execute("SELECT name FROM Pokemon WHERE pokedex_number = ?", (pokemon_id,))
                        pokemon_name = cursor.fetchone()[0]
                        
                        print(f"  Added {move_name} to {pokemon_name} (learned from {pre_evo_name} at level {level_learned})")
                        
                except sqlite3.Error as e:
                    print(f"  Error adding move {move_id} to Pokemon {pokemon_id}: {e}")
    
    conn.commit()
    
    print(f"\nUpdate complete! Added {moves_added} moves from pre-evolutions.")
    
    # Show some examples of the updated data
    print("\nExamples of moves inherited from pre-evolutions:")
    cursor.execute("""
        SELECT DISTINCT 
            p.name as pokemon_name,
            m.name as move_name,
            pm.level_learned,
            pe.name as pre_evo_name
        FROM PokemonMoves pm
        JOIN Pokemon p ON pm.pokemon_id = p.pokedex_number
        JOIN Moves m ON pm.move_id = m.id
        JOIN Evolution e ON e.to_pokemon_id = p.pokedex_number
        JOIN Pokemon pe ON e.from_pokemon_id = pe.pokedex_number
        JOIN PokemonMoves pm_pre ON pm_pre.pokemon_id = pe.pokedex_number AND pm_pre.move_id = m.id
        WHERE pm.level_learned = pm_pre.level_learned
        ORDER BY p.pokedex_number, pm.level_learned
        LIMIT 15
    """)
    
    for row in cursor.fetchall():
        pokemon_name, move_name, level, pre_evo_name = row
        print(f"{pokemon_name} can learn {move_name} at level {level} (inherited from {pre_evo_name})")
    
    # Show total move counts before and after
    print(f"\nTotal moves in PokemonMoves table:")
    cursor.execute("SELECT COUNT(*) FROM PokemonMoves")
    total_moves = cursor.fetchone()[0]
    print(f"Total entries: {total_moves}")
    
    # Show some evolution examples
    print(f"\nEvolution chain examples:")
    cursor.execute("""
        SELECT 
            pe.name as pre_evo,
            p.name as evolution,
            e.evolution_method,
            e.minimum_level
        FROM Evolution e
        JOIN Pokemon pe ON e.from_pokemon_id = pe.pokedex_number
        JOIN Pokemon p ON e.to_pokemon_id = p.pokedex_number
        ORDER BY pe.pokedex_number
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        pre_evo, evolution, method, level = row
        if level:
            print(f"{pre_evo} -> {evolution} (via {method} at level {level})")
        else:
            print(f"{pre_evo} -> {evolution} (via {method})")
    
    conn.close()

if __name__ == "__main__":
    main()
