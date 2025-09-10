import requests

# Get all Gen 1 pokemon species from PokeAPI
gen1_url = "https://pokeapi.co/api/v2/generation/1/"
gen1 = requests.get(gen1_url).json()
pokemon_urls = [p['url'] for p in gen1['pokemon_species']]

insert_lines = []
for url in pokemon_urls:
    species = requests.get(url).json()
    # Get pokedex number, name, and flavor text (entry)
    pokedex_number = species['id']
    name = species['name'].capitalize().replace("'", "''")
    # Get the English flavor text
    entry = next((ft['flavor_text'].replace("\n", " ").replace("\f", " ").replace("'", "''")
                  for ft in species['flavor_text_entries'] if ft['language']['name'] == 'en'), '')
    # Get details from the pokemon endpoint for base stats and types
    poke_url = f"https://pokeapi.co/api/v2/pokemon/{pokedex_number}/"
    poke = requests.get(poke_url).json()
    types = [t['type']['name'].capitalize() for t in poke['types']]
    type1 = types[0] if len(types) > 0 else 'NULL'
    type2 = types[1] if len(types) > 1 else 'NULL'
    stats = {s['stat']['name']: s['base_stat'] for s in poke['stats']}
    base_hp = stats.get('hp', 'NULL')
    base_attack = stats.get('attack', 'NULL')
    base_defense = stats.get('defense', 'NULL')
    base_special = stats.get('special-attack', stats.get('special', 'NULL'))
    base_speed = stats.get('speed', 'NULL')
    if type2 == 'NULL':
        type2_sql = 'NULL'
    else:
        type2_sql = f"'{type2}'"
    insert_lines.append(
        f"INSERT INTO Pokemon (pokedex_number, name, type1, type2, base_hp, base_attack, base_defense, base_special, base_speed, entry) "
        f"VALUES ({pokedex_number}, '{name}', '{type1}', {type2_sql}, {base_hp}, {base_attack}, {base_defense}, {base_special}, {base_speed}, '{entry}');"
    )

with open('gen1_pokemon_inserts.sql', 'w') as f:
    f.write('\n'.join(insert_lines))

print(f"Generated {len(insert_lines)} SQL insert statements for Gen 1 Pokémon.")
