#!/usr/bin/env python3
"""
Fetch Pokemon evolution data from PokeAPI for Generation 1 Pokemon
and populate the Evolution table.
"""

import sqlite3
import requests
import time
from typing import Dict, List, Optional

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

def main():
    # Connect to database
    conn = sqlite3.connect('pokemon.db')
    cursor = conn.cursor()
    
    # Get all Gen 1 Pokemon (1-151)
    gen1_pokemon = range(1, 152)
    processed_chains = set()
    all_evolutions = []
    
    print("Fetching evolution data for Generation 1 Pokemon...")
    
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
                
                print(f"Added evolution: {evolution['from_pokemon_id']} -> {evolution['to_pokemon_id']} "
                      f"({evolution['evolution_method']})")
                
            except sqlite3.Error as e:
                print(f"Error inserting evolution {evolution['from_pokemon_id']} -> {evolution['to_pokemon_id']}: {e}")
    
    conn.commit()
    
    # Verify the data
    cursor.execute("SELECT COUNT(*) FROM Evolution")
    count = cursor.fetchone()[0]
    print(f"Total evolution relationships inserted: {count}")
    
    # Show some examples
    print("\nSample evolution data:")
    cursor.execute("""
        SELECT e.from_pokemon_id, p1.name as from_name, 
               e.to_pokemon_id, p2.name as to_name,
               e.evolution_method, e.minimum_level, e.evolution_item
        FROM Evolution e
        JOIN Pokemon p1 ON e.from_pokemon_id = p1.pokedex_number
        JOIN Pokemon p2 ON e.to_pokemon_id = p2.pokedex_number
        ORDER BY e.from_pokemon_id
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        from_id, from_name, to_id, to_name, method, level, item = row
        evolution_info = f"{method}"
        if level:
            evolution_info += f" at level {level}"
        if item:
            evolution_info += f" with {item}"
        print(f"{from_name} (#{from_id}) -> {to_name} (#{to_id}) via {evolution_info}")
    
    conn.close()
    print("Evolution data setup complete!")

if __name__ == "__main__":
    main()
