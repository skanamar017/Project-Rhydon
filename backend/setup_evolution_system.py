#!/usr/bin/env python3
"""
Complete Evolution System Setup Script

This script sets up the entire Pokemon evolution system including:
1. Creating the Evolution table
2. Fetching evolution data from PokeAPI
3. Updating Pokemon moves to include pre-evolution moves

Run this script whenever you reset the database to restore the complete
evolution-aware move system.
"""

import sqlite3
import requests
import time
import os
from typing import Dict, List, Optional

def create_evolution_table(conn):
    """Create the Evolution table with proper schema"""
    print("Creating Evolution table...")
    
    cursor = conn.cursor()
    
    # Create Evolution table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Evolution (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_pokemon_id INTEGER NOT NULL,
            to_pokemon_id INTEGER NOT NULL,
            evolution_method TEXT,
            minimum_level INTEGER,
            evolution_item TEXT,
            trade_required BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (from_pokemon_id) REFERENCES Pokemon(pokedex_number),
            FOREIGN KEY (to_pokemon_id) REFERENCES Pokemon(pokedex_number),
            UNIQUE(from_pokemon_id, to_pokemon_id)
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_evolution_from ON Evolution(from_pokemon_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_evolution_to ON Evolution(to_pokemon_id)")
    
    conn.commit()
    print("Evolution table created successfully!")

def get_pokemon_species_data(pokemon_id: int) -> Optional[Dict]:
    """Get species data for a Pokemon from PokeAPI"""
    try:
        url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching species data for Pokemon {pokemon_id}: {e}")
        return None

def get_evolution_chain(chain_url: str) -> Optional[Dict]:
    """Get evolution chain data from PokeAPI"""
    try:
        response = requests.get(chain_url)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error fetching evolution chain from {chain_url}: {e}")
        return None

def extract_pokemon_id_from_url(url: str) -> int:
    """Extract Pokemon ID from PokeAPI URL"""
    return int(url.rstrip('/').split('/')[-1])

def parse_evolution_chain(chain_data: Dict) -> List[Dict]:
    """Parse evolution chain data and extract evolution relationships"""
    evolutions = []
    
    def process_chain_link(chain_link: Dict, from_pokemon_id: Optional[int] = None):
        current_pokemon_id = extract_pokemon_id_from_url(chain_link['species']['url'])
        
        # If this isn't the base form, add evolution relationship
        if from_pokemon_id is not None:
            for evolution_detail in chain_link['evolution_details']:
                evolution_method = "level"
                minimum_level = evolution_detail.get('min_level')
                evolution_item = None
                trade_required = False
                
                # Determine evolution method
                if evolution_detail.get('item'):
                    evolution_method = "item"
                    evolution_item = evolution_detail['item']['name']
                elif evolution_detail.get('trade_species'):
                    evolution_method = "trade"
                    trade_required = True
                elif evolution_detail.get('needs_overworld_rain'):
                    evolution_method = "other"
                elif evolution_detail.get('time_of_day'):
                    evolution_method = "level_time"
                
                evolutions.append({
                    'from_pokemon_id': from_pokemon_id,
                    'to_pokemon_id': current_pokemon_id,
                    'evolution_method': evolution_method,
                    'minimum_level': minimum_level,
                    'evolution_item': evolution_item,
                    'trade_required': trade_required
                })
        
        # Process next evolutions
        for next_evolution in chain_link.get('evolves_to', []):
            process_chain_link(next_evolution, current_pokemon_id)
    
    process_chain_link(chain_data['chain'])
    return evolutions

def fetch_evolution_data(conn):
    """Fetch and populate evolution data from PokeAPI"""
    print("Fetching evolution data from PokeAPI...")
    
    cursor = conn.cursor()
    
    # Clear existing evolution data
    cursor.execute("DELETE FROM Evolution")
    conn.commit()
    
    # Get all Gen 1 Pokemon (1-151)
    gen1_pokemon = range(1, 152)
    processed_chains = set()
    all_evolutions = []
    
    for pokemon_id in gen1_pokemon:
        print(f"Processing Pokemon #{pokemon_id}...")
        
        # Get species data
        species_data = get_pokemon_species_data(pokemon_id)
        if not species_data:
            continue
        
        # Get evolution chain URL
        evolution_chain_url = species_data['evolution_chain']['url']
        chain_id = evolution_chain_url.rstrip('/').split('/')[-1]
        
        # Skip if we've already processed this chain
        if chain_id in processed_chains:
            continue
        
        processed_chains.add(chain_id)
        
        # Get evolution chain data
        chain_data = get_evolution_chain(evolution_chain_url)
        if not chain_data:
            continue
        
        # Parse evolution relationships
        evolutions = parse_evolution_chain(chain_data)
        all_evolutions.extend(evolutions)
        
        # Rate limiting
        time.sleep(0.1)
    
    print(f"Found {len(all_evolutions)} evolution relationships")
    
    # Insert evolution data into database
    print("Inserting evolution data into database...")
    
    inserted_count = 0
    for evolution in all_evolutions:
        # Only include Gen 1 Pokemon (1-151)
        if (evolution['from_pokemon_id'] <= 151 and 
            evolution['to_pokemon_id'] <= 151):
            
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO Evolution 
                    (from_pokemon_id, to_pokemon_id, evolution_method, minimum_level, evolution_item, trade_required)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    evolution['from_pokemon_id'],
                    evolution['to_pokemon_id'],
                    evolution['evolution_method'],
                    evolution['minimum_level'],
                    evolution['evolution_item'],
                    evolution['trade_required']
                ))
                
                if cursor.rowcount > 0:
                    inserted_count += 1
                
            except sqlite3.Error as e:
                print(f"Error inserting evolution {evolution['from_pokemon_id']} -> {evolution['to_pokemon_id']}: {e}")
    
    conn.commit()
    print(f"Inserted {inserted_count} evolution relationships")

def get_evolution_chain_for_pokemon(cursor, pokemon_id: int) -> List[int]:
    """Get the full evolution chain leading to a Pokemon (including itself)"""
    chain = []
    
    # Recursively find all pre-evolutions
    def find_pre_evolutions(current_id: int, visited: set):
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

def update_pokemon_moves_with_evolutions(conn):
    """Update PokemonMoves table to include moves from previous evolutions"""
    print("Updating Pokemon moves to include pre-evolution moves...")
    
    cursor = conn.cursor()
    
    # Get all Pokemon
    cursor.execute("SELECT pokedex_number FROM Pokemon ORDER BY pokedex_number")
    all_pokemon = [row[0] for row in cursor.fetchall()]
    
    moves_added = 0
    
    for pokemon_id in all_pokemon:
        print(f"Processing Pokemon #{pokemon_id}...")
        
        # Get evolution chain (all pre-evolutions and current Pokemon)
        evolution_chain = get_evolution_chain_for_pokemon(cursor, pokemon_id)
        
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
                        
                except sqlite3.Error as e:
                    print(f"  Error adding move {move_id} to Pokemon {pokemon_id}: {e}")
    
    conn.commit()
    print(f"Added {moves_added} moves from pre-evolutions")

def verify_setup(conn):
    """Verify that the evolution system was set up correctly"""
    print("\nVerifying evolution system setup...")
    
    cursor = conn.cursor()
    
    # Check Evolution table
    cursor.execute("SELECT COUNT(*) FROM Evolution")
    evolution_count = cursor.fetchone()[0]
    print(f"✅ Evolution relationships: {evolution_count}")
    
    # Check total moves in PokemonMoves
    cursor.execute("SELECT COUNT(*) FROM PokemonMoves")
    total_moves = cursor.fetchone()[0]
    print(f"✅ Total Pokemon-Move relationships: {total_moves}")
    
    # Show some examples
    print("\n📋 Sample evolution data:")
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
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        pre_evo, evolution, method, level = row
        if level:
            print(f"   {pre_evo} → {evolution} (via {method} at level {level})")
        else:
            print(f"   {pre_evo} → {evolution} (via {method})")
    
    # Test specific case: Charizard move count
    cursor.execute("""
        SELECT COUNT(*) FROM PokemonMoves 
        WHERE pokemon_id = 6
    """)
    charizard_moves = cursor.fetchone()[0]
    print(f"\n🔥 Charizard total moves: {charizard_moves}")

def main():
    """Main setup function"""
    print("🚀 Starting Pokemon Evolution System Setup")
    print("=" * 50)
    
    # Check if database exists
    db_path = "pokemon.db"
    if not os.path.exists(db_path):
        print(f"❌ Error: Database file '{db_path}' not found!")
        print("Please make sure you're running this script from the backend directory")
        print("and that the Pokemon database has been created.")
        return
    
    # Connect to database
    try:
        conn = sqlite3.connect(db_path)
        print(f"✅ Connected to database: {db_path}")
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return
    
    try:
        # Step 1: Create Evolution table
        create_evolution_table(conn)
        
        # Step 2: Fetch evolution data from PokeAPI
        fetch_evolution_data(conn)
        
        # Step 3: Update Pokemon moves with pre-evolution moves
        update_pokemon_moves_with_evolutions(conn)
        
        # Step 4: Verify setup
        verify_setup(conn)
        
        print("\n🎉 Evolution system setup completed successfully!")
        print("\nYour Pokemon now know moves from their pre-evolutions!")
        print("You can test this with the new API endpoint:")
        print("  GET /Pokemon/{id}/moves/with_evolutions")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
        print("\n📝 Database connection closed")

if __name__ == "__main__":
    main()
