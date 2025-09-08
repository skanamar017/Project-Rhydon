import requests
import time

# Get all Gen 1 pokemon species from PokeAPI
gen1_url = "https://pokeapi.co/api/v2/generation/1/"
gen1 = requests.get(gen1_url).json()
pokemon_urls = [p['url'] for p in gen1['pokemon_species']]

# Build a mapping from move name to move_id (assuming Moves table is already populated)
# You may need to adjust this if your move IDs are not sequential or start at 1
move_name_to_id = {}
move_id = 1
moves_url = "https://pokeapi.co/api/v2/generation/1/"
gen1_moves = requests.get(moves_url).json()['moves']
for m in gen1_moves:
    move_name_to_id[m['name']] = move_id
    move_id += 1

insert_lines = []
for url in pokemon_urls:
    species = requests.get(url).json()
    pokedex_number = species['id']
    poke_url = f"https://pokeapi.co/api/v2/pokemon/{pokedex_number}/"
    poke = requests.get(poke_url).json()
    pokemon_id = pokedex_number  # Assumes your Pokemon table uses pokedex_number as id
    for move in poke['moves']:
        move_name = move['move']['name']
        if move_name not in move_name_to_id:
            continue
        for vgd in move['version_group_details']:
            vg = vgd['version_group']['name']
            if vg in ['red-blue', 'yellow']:
                method = vgd['move_learn_method']['name']
                level = vgd['level_learned_at']
                # Only include moves that are learnable in Gen 1
                insert_lines.append(f"INSERT INTO PokemonMoves (pokemon_id, move_id, level_learned) VALUES ({pokemon_id}, {move_name_to_id[move_name]}, {level}); -- {move_name} ({method})")
    time.sleep(0.2)  # Be nice to the API

with open('gen1_pokemon_moves_inserts.sql', 'w') as f:
    f.write('\n'.join(insert_lines))

print(f"Generated {len(insert_lines)} SQL insert statements for Gen 1 PokemonMoves.")
