import requests

# Get all Gen 1 moves from PokeAPI
gen1_url = "https://pokeapi.co/api/v2/generation/1/"
gen1 = requests.get(gen1_url).json()
move_urls = [m['url'] for m in gen1['moves']]

insert_lines = []
for url in move_urls:
    move = requests.get(url).json()
    name = move['name'].replace("'", "''")
    type_ = move['type']['name'].capitalize()
    power = move['power'] if move['power'] is not None else 'NULL'
    accuracy = move['accuracy'] if move['accuracy'] is not None else 'NULL'
    pp = move['pp'] if move['pp'] is not None else 'NULL'
    
    # Get effect description (use English flavor text)
    effect = "No description available"
    if 'effect_entries' in move and move['effect_entries']:
        for entry in move['effect_entries']:
            if entry['language']['name'] == 'en':
                effect = entry['effect'].replace("'", "''").replace('\n', ' ').strip()
                break
    elif 'flavor_text_entries' in move and move['flavor_text_entries']:
        # Fallback to flavor text if no effect entries
        for entry in move['flavor_text_entries']:
            if entry['language']['name'] == 'en':
                effect = entry['flavor_text'].replace("'", "''").replace('\n', ' ').strip()
                break
    
    # Only insert moves with a valid type (Gen 1 types)
    if type_ in [
        'Normal','Fire','Water','Grass','Electric','Ice','Fighting','Poison','Ground','Flying','Psychic','Bug','Rock','Ghost','Dragon']:
        insert_lines.append(f"INSERT INTO Moves (name, type, power, accuracy, pp, effect) VALUES ('{name}', '{type_}', {power}, {accuracy}, {pp}, '{effect}');")

with open('gen1_moves_inserts.sql', 'w') as f:
    f.write('\n'.join(insert_lines))

print(f"Generated {len(insert_lines)} SQL insert statements for Gen 1 moves with effects.")
