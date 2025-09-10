import requests
import time
import sqlite3

def get_move_id_from_db(move_name, cursor):
    """Get move ID from database by name"""
    cursor.execute("SELECT id FROM Moves WHERE name = ?", (move_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def clear_pokemon_moves_table():
    """Clear existing PokemonMoves data"""
    conn = sqlite3.connect('pokemon.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM PokemonMoves")
    conn.commit()
    conn.close()
    print("Cleared existing PokemonMoves data")

def main():
    # Clear existing data
    clear_pokemon_moves_table()
    
    # Connect to database to get move IDs
    conn = sqlite3.connect('pokemon.db')
    cursor = conn.cursor()
    
    # Get all Gen 1 pokemon species from PokeAPI
    print("Fetching Gen 1 Pokemon list...")
    gen1_url = "https://pokeapi.co/api/v2/generation/1/"
    gen1 = requests.get(gen1_url).json()
    pokemon_species = gen1['pokemon_species']
    
    insert_lines = []
    total_pokemon = len(pokemon_species)
    
    for i, species_data in enumerate(pokemon_species):
        pokedex_number = species_data['url'].split('/')[-2]
        print(f"Processing Pokemon {i+1}/{total_pokemon}: Pokedex #{pokedex_number}")
        
        # Get the Pokemon data
        poke_url = f"https://pokeapi.co/api/v2/pokemon/{pokedex_number}/"
        try:
            poke = requests.get(poke_url).json()
        except:
            print(f"Error fetching data for Pokemon #{pokedex_number}")
            continue
            
        pokemon_id = int(pokedex_number)  # Uses pokedex_number as pokemon_id
        
        for move_data in poke['moves']:
            move_name = move_data['move']['name']
            move_id = get_move_id_from_db(move_name, cursor)
            
            if not move_id:
                continue  # Skip moves not in our database
                
            # Check version group details for Red/Blue specifically
            for vgd in move_data['version_group_details']:
                version_group = vgd['version_group']['name']
                
                # Only process Red/Blue version data
                if version_group == 'red-blue':
                    method = vgd['move_learn_method']['name']
                    level = vgd['level_learned_at']
                    
                    # Include level-up moves and TM/HM moves (level 0)
                    if method in ['level-up', 'machine']:
                        insert_lines.append(f"INSERT INTO PokemonMoves (pokemon_id, move_id, level_learned) VALUES ({pokemon_id}, {move_id}, {level}); -- {move_name} ({method})")
        
        time.sleep(0.1)  # Be nice to the API
    
    conn.close()
    
    # Write SQL file
    with open('gen1_pokemon_moves_inserts_corrected.sql', 'w') as f:
        f.write('\n'.join(insert_lines))
    
    print(f"Generated {len(insert_lines)} SQL insert statements for Gen 1 PokemonMoves.")
    
    # Execute the inserts
    print("Inserting data into database...")
    conn = sqlite3.connect('pokemon.db')
    cursor = conn.cursor()
    
    for line in insert_lines:
        sql_command = line.split(';')[0] + ';'  # Remove comments
        try:
            cursor.execute(sql_command)
        except Exception as e:
            print(f"Error executing: {sql_command}")
            print(f"Error: {e}")
    
    conn.commit()
    conn.close()
    print("Database updated successfully!")

if __name__ == "__main__":
    main()
