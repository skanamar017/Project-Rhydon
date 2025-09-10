"""
Comprehensive Pokemon Database Setup
====================================

This file consolidates all database creation, data population, and evolution system setup
into a single comprehensive script. It includes:

1. Database schema creation (tables)
2. Pokemon data population 
3. Moves data population
4. Pokemon-Moves relationships
5. Evolution system setup
6. Data validation and verification

Run this script to completely set up your Pokemon database from scratch.
"""

import sqlite3
import requests
import time
import os
from typing import Dict, List, Optional, Set
import json

class PokemonDatabaseSetup:
    def __init__(self, db_path: str = "pokemon.db"):
        self.db_path = db_path
        self.base_url = "https://pokeapi.co/api/v2"
        
    def setup_complete_database(self, force_recreate: bool = False):
        """Complete database setup from scratch"""
        print("🚀 Starting Complete Pokemon Database Setup")
        print("=" * 60)
        
        if force_recreate and os.path.exists(self.db_path):
            os.remove(self.db_path)
            print(f"🗑️  Removed existing database: {self.db_path}")
        
        # Step 1: Create database and tables
        self.create_database_schema()
        
        # Step 2: Populate Pokemon data
        self.populate_pokemon_data()
        
        # Step 3: Populate moves data
        self.populate_moves_data()
        
        # Step 4: Populate Pokemon-Moves relationships
        self.populate_pokemon_moves()
        
        # Step 5: Set up evolution system
        self.setup_evolution_system()
        
        # Step 6: Verify setup
        self.verify_database()
        
        print("\n🎉 Complete database setup finished!")
        print("Your Pokemon database is ready to use!")

    def create_database_schema(self):
        """Create all database tables"""
        print("\n📋 Creating database schema...")
        
        with sqlite3.connect(self.db_path) as conn:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Pokemon Types
            conn.execute("""
                CREATE TABLE IF NOT EXISTS PokemonType (
                    type_name VARCHAR(20) PRIMARY KEY
                )
            """)
            
            # Insert Pokemon types
            types = ['Normal', 'Fire', 'Water', 'Grass', 'Electric', 'Ice', 
                    'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 
                    'Bug', 'Rock', 'Ghost', 'Dragon', 'Fairy']
            
            for ptype in types:
                conn.execute("INSERT OR IGNORE INTO PokemonType (type_name) VALUES (?)", (ptype,))
            
            # Pokemon table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Pokemon (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pokedex_number INTEGER UNIQUE NOT NULL,
                    name VARCHAR(50) NOT NULL,
                    type1 VARCHAR(20) NOT NULL,
                    type2 VARCHAR(20),
                    base_hp INTEGER NOT NULL,
                    base_attack INTEGER NOT NULL,
                    base_defense INTEGER NOT NULL,
                    base_special INTEGER NOT NULL,
                    base_speed INTEGER NOT NULL,
                    entry TEXT,
                    FOREIGN KEY (type1) REFERENCES PokemonType(type_name),
                    FOREIGN KEY (type2) REFERENCES PokemonType(type_name)
                )
            """)
            
            # Moves table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Moves (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    type VARCHAR(20) NOT NULL,
                    power INTEGER,
                    accuracy INTEGER,
                    pp INTEGER,
                    effect TEXT,
                    FOREIGN KEY (type) REFERENCES PokemonType(type_name)
                )
            """)
            
            # Pokemon-Moves relationship
            conn.execute("""
                CREATE TABLE IF NOT EXISTS PokemonMoves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pokemon_id INTEGER NOT NULL,
                    move_id INTEGER NOT NULL,
                    level_learned INTEGER NOT NULL,
                    FOREIGN KEY (pokemon_id) REFERENCES Pokemon(pokedex_number),
                    FOREIGN KEY (move_id) REFERENCES Moves(id),
                    UNIQUE(pokemon_id, move_id, level_learned)
                )
            """)
            
            # Team table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS Team (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL
                )
            """)
            
            # TeamPokemon table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS TeamPokemon (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_id INTEGER NOT NULL,
                    pokemon_id INTEGER NOT NULL,
                    nickname VARCHAR(50),
                    level INTEGER NOT NULL CHECK(level >= 1 AND level <= 100),
                    iv_attack INTEGER DEFAULT 0 CHECK(iv_attack >= 0 AND iv_attack <= 15),
                    iv_defense INTEGER DEFAULT 0 CHECK(iv_defense >= 0 AND iv_defense <= 15),
                    iv_speed INTEGER DEFAULT 0 CHECK(iv_speed >= 0 AND iv_speed <= 15),
                    iv_special INTEGER DEFAULT 0 CHECK(iv_special >= 0 AND iv_special <= 15),
                    ev_hp INTEGER DEFAULT 0 CHECK(ev_hp >= 0 AND ev_hp <= 65535),
                    ev_attack INTEGER DEFAULT 0 CHECK(ev_attack >= 0 AND ev_attack <= 65535),
                    ev_defense INTEGER DEFAULT 0 CHECK(ev_defense >= 0 AND ev_defense <= 65535),
                    ev_speed INTEGER DEFAULT 0 CHECK(ev_speed >= 0 AND ev_speed <= 65535),
                    ev_special INTEGER DEFAULT 0 CHECK(ev_special >= 0 AND ev_special <= 65535),
                    current_hp INTEGER,
                    status VARCHAR(20) DEFAULT 'Healthy',
                    move1_id INTEGER,
                    move2_id INTEGER,
                    move3_id INTEGER,
                    move4_id INTEGER,
                    FOREIGN KEY (team_id) REFERENCES Team(id) ON DELETE CASCADE,
                    FOREIGN KEY (pokemon_id) REFERENCES Pokemon(pokedex_number),
                    FOREIGN KEY (move1_id) REFERENCES Moves(id),
                    FOREIGN KEY (move2_id) REFERENCES Moves(id),
                    FOREIGN KEY (move3_id) REFERENCES Moves(id),
                    FOREIGN KEY (move4_id) REFERENCES Moves(id)
                )
            """)
            
            # Evolution table
            conn.execute("""
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
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_pokedex ON Pokemon(pokedex_number)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_moves_pokemon ON PokemonMoves(pokemon_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pokemon_moves_move ON PokemonMoves(move_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_evolution_from ON Evolution(from_pokemon_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_evolution_to ON Evolution(to_pokemon_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_team_pokemon_team ON TeamPokemon(team_id)")
            
            conn.commit()
            
        print("✅ Database schema created successfully!")

    def populate_pokemon_data(self):
        """Fetch and populate Generation 1 Pokemon data from PokeAPI"""
        print("\n🔍 Fetching Pokemon data from PokeAPI...")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM Pokemon")  # Clear existing data
            
            for pokemon_id in range(1, 152):  # Gen 1: 1-151
                try:
                    print(f"  Fetching Pokemon #{pokemon_id}...")
                    
                    # Get Pokemon data
                    response = requests.get(f"{self.base_url}/pokemon/{pokemon_id}")
                    if response.status_code != 200:
                        continue
                        
                    pokemon_data = response.json()
                    
                    # Get species data for description
                    species_response = requests.get(f"{self.base_url}/pokemon-species/{pokemon_id}")
                    species_data = species_response.json() if species_response.status_code == 200 else {}
                    
                    # Extract basic info
                    name = pokemon_data['name'].title()
                    pokedex_number = pokemon_data['id']
                    
                    # Extract types
                    types = [t['type']['name'].title() for t in pokemon_data['types']]
                    type1 = types[0] if types else 'Normal'
                    type2 = types[1] if len(types) > 1 else None
                    
                    # Handle Fairy type (not in Gen 1 originally, but Clefairy line should be Fairy)
                    if name in ['Clefairy', 'Clefable']:
                        type1 = 'Fairy'
                        type2 = None
                    
                    # Extract base stats
                    stats = {stat['stat']['name']: stat['base_stat'] for stat in pokemon_data['stats']}
                    base_hp = stats.get('hp', 50)
                    base_attack = stats.get('attack', 50)
                    base_defense = stats.get('defense', 50)
                    base_speed = stats.get('speed', 50)
                    # In Gen 1, Special Attack and Special Defense were combined as "Special"
                    base_special = stats.get('special-attack', 50)
                    
                    # Extract Pokedex entry (English)
                    entry = ""
                    if 'flavor_text_entries' in species_data:
                        for entry_data in species_data['flavor_text_entries']:
                            if entry_data['language']['name'] == 'en':
                                entry = entry_data['flavor_text'].replace('\n', ' ').replace('\f', ' ')
                                break
                    
                    # Insert into database
                    conn.execute("""
                        INSERT OR REPLACE INTO Pokemon 
                        (pokedex_number, name, type1, type2, base_hp, base_attack, base_defense, base_special, base_speed, entry)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (pokedex_number, name, type1, type2, base_hp, base_attack, base_defense, base_special, base_speed, entry))
                    
                    # Rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"    Error fetching Pokemon #{pokemon_id}: {e}")
                    continue
            
            conn.commit()
            
        print("✅ Pokemon data populated successfully!")

    def populate_moves_data(self):
        """Fetch and populate Generation 1 moves data"""
        print("\n🎯 Fetching moves data from PokeAPI...")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM Moves")  # Clear existing data
            
            # Get Generation 1 moves (moves 1-165 approximately)
            gen1_moves = []
            
            # Get version group for Red/Blue
            version_response = requests.get(f"{self.base_url}/version-group/1")  # Red/Blue
            if version_response.status_code == 200:
                version_data = version_response.json()
                
                # Get moves from this generation
                for move_url in version_data['move_learn_methods'][0]['version_group_details']:
                    # This approach is complex, let's use a simpler method
                    pass
            
            # Simpler approach: get moves 1-165 (known Gen 1 range)
            for move_id in range(1, 166):
                try:
                    print(f"  Fetching move #{move_id}...")
                    
                    response = requests.get(f"{self.base_url}/move/{move_id}")
                    if response.status_code != 200:
                        continue
                        
                    move_data = response.json()
                    
                    # Check if move exists in Generation 1
                    gen1_games = ['red', 'blue', 'yellow']
                    is_gen1 = False
                    for game_index in move_data.get('game_indices', []):
                        if game_index['version']['name'] in gen1_games:
                            is_gen1 = True
                            break
                    
                    if not is_gen1:
                        continue
                    
                    # Extract move info
                    name = move_data['name'].replace('-', ' ').title()
                    move_type = move_data['type']['name'].title()
                    power = move_data['power']
                    accuracy = move_data['accuracy']
                    pp = move_data['pp']
                    
                    # Get effect description
                    effect = ""
                    if move_data.get('effect_entries'):
                        for effect_entry in move_data['effect_entries']:
                            if effect_entry['language']['name'] == 'en':
                                effect = effect_entry['short_effect']
                                break
                    
                    # Insert into database
                    conn.execute("""
                        INSERT OR REPLACE INTO Moves (id, name, type, power, accuracy, pp, effect)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (move_id, name, move_type, power, accuracy, pp, effect))
                    
                    # Rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"    Error fetching move #{move_id}: {e}")
                    continue
            
            conn.commit()
            
        print("✅ Moves data populated successfully!")

    def populate_pokemon_moves(self):
        """Fetch and populate Pokemon-Moves relationships"""
        print("\n🔗 Fetching Pokemon-Moves relationships...")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM PokemonMoves")  # Clear existing data
            
            for pokemon_id in range(1, 152):
                try:
                    print(f"  Fetching moves for Pokemon #{pokemon_id}...")
                    
                    response = requests.get(f"{self.base_url}/pokemon/{pokemon_id}")
                    if response.status_code != 200:
                        continue
                        
                    pokemon_data = response.json()
                    
                    # Process moves
                    for move_entry in pokemon_data['moves']:
                        move_id = int(move_entry['move']['url'].split('/')[-2])
                        
                        # Get move learning details for Red/Blue
                        for version_detail in move_entry['version_group_details']:
                            if version_detail['version_group']['name'] in ['red-blue', 'yellow']:
                                level_learned = version_detail['level_learned_at']
                                learn_method = version_detail['move_learn_method']['name']
                                
                                # Convert learn method to level
                                if learn_method == 'level-up':
                                    level = level_learned
                                elif learn_method in ['machine', 'tutor']:
                                    level = 0  # TM/HM moves
                                else:
                                    continue  # Skip other methods
                                
                                # Insert relationship
                                conn.execute("""
                                    INSERT OR IGNORE INTO PokemonMoves (pokemon_id, move_id, level_learned)
                                    VALUES (?, ?, ?)
                                """, (pokemon_id, move_id, level))
                                break  # Use first valid entry
                    
                    # Rate limiting
                    time.sleep(0.2)
                    
                except Exception as e:
                    print(f"    Error fetching moves for Pokemon #{pokemon_id}: {e}")
                    continue
            
            conn.commit()
            
        print("✅ Pokemon-Moves relationships populated successfully!")

    def setup_evolution_system(self):
        """Set up the evolution system with PokeAPI data"""
        print("\n🔄 Setting up evolution system...")
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM Evolution")  # Clear existing data
            
            # Process evolution chains
            processed_chains = set()
            all_evolutions = []
            
            for pokemon_id in range(1, 152):
                try:
                    print(f"  Processing evolution chain for Pokemon #{pokemon_id}...")
                    
                    # Get species data
                    species_response = requests.get(f"{self.base_url}/pokemon-species/{pokemon_id}")
                    if species_response.status_code != 200:
                        continue
                        
                    species_data = species_response.json()
                    
                    # Get evolution chain URL
                    evolution_chain_url = species_data['evolution_chain']['url']
                    chain_id = evolution_chain_url.rstrip('/').split('/')[-1]
                    
                    # Skip if already processed
                    if chain_id in processed_chains:
                        continue
                        
                    processed_chains.add(chain_id)
                    
                    # Get evolution chain data
                    chain_response = requests.get(evolution_chain_url)
                    if chain_response.status_code != 200:
                        continue
                        
                    chain_data = chain_response.json()
                    
                    # Parse evolution relationships
                    evolutions = self._parse_evolution_chain(chain_data)
                    all_evolutions.extend(evolutions)
                    
                    # Rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"    Error processing evolution for Pokemon #{pokemon_id}: {e}")
                    continue
            
            # Insert evolution data
            inserted_count = 0
            for evolution in all_evolutions:
                # Only include Gen 1 Pokemon (1-151)
                if (evolution['from_pokemon_id'] <= 151 and 
                    evolution['to_pokemon_id'] <= 151):
                    
                    try:
                        conn.execute("""
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
                        
                        if conn.cursor().rowcount > 0:
                            inserted_count += 1
                            
                    except sqlite3.Error as e:
                        print(f"      Error inserting evolution: {e}")
            
            conn.commit()
            
            # Update Pokemon moves with pre-evolution moves
            self._update_pokemon_moves_with_evolutions(conn)
            
        print(f"✅ Evolution system set up with {inserted_count} relationships!")

    def _parse_evolution_chain(self, chain_data: Dict) -> List[Dict]:
        """Parse evolution chain data from PokeAPI"""
        evolutions = []
        
        def extract_pokemon_id(url: str) -> int:
            return int(url.rstrip('/').split('/')[-1])
        
        def process_chain_link(chain_link: Dict, from_pokemon_id: Optional[int] = None):
            current_pokemon_id = extract_pokemon_id(chain_link['species']['url'])
            
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
                    elif evolution_detail.get('trade_species') or evolution_detail.get('held_item'):
                        evolution_method = "trade"
                        trade_required = True
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

    def _update_pokemon_moves_with_evolutions(self, conn):
        """Add moves from pre-evolutions to evolved Pokemon"""
        print("  Updating Pokemon moves with pre-evolution moves...")
        
        cursor = conn.cursor()
        
        # Get all Pokemon
        cursor.execute("SELECT pokedex_number FROM Pokemon ORDER BY pokedex_number")
        all_pokemon = [row[0] for row in cursor.fetchall()]
        
        moves_added = 0
        
        for pokemon_id in all_pokemon:
            # Get evolution chain
            evolution_chain = self._get_evolution_chain_for_pokemon(cursor, pokemon_id)
            
            if len(evolution_chain) <= 1:
                continue  # No pre-evolutions
            
            # Get current moves
            cursor.execute("""
                SELECT move_id, level_learned FROM PokemonMoves 
                WHERE pokemon_id = ?
            """, (pokemon_id,))
            current_moves = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Add moves from pre-evolutions
            for pre_evo_id in evolution_chain[:-1]:  # Exclude current Pokemon
                cursor.execute("""
                    SELECT move_id, level_learned FROM PokemonMoves 
                    WHERE pokemon_id = ?
                """, (pre_evo_id,))
                
                for move_id, level_learned in cursor.fetchall():
                    if move_id not in current_moves:
                        # Check if move exists
                        cursor.execute("SELECT id FROM Moves WHERE id = ?", (move_id,))
                        if cursor.fetchone():
                            try:
                                cursor.execute("""
                                    INSERT OR IGNORE INTO PokemonMoves (pokemon_id, move_id, level_learned)
                                    VALUES (?, ?, ?)
                                """, (pokemon_id, move_id, level_learned))
                                
                                if cursor.rowcount > 0:
                                    moves_added += 1
                                    
                            except sqlite3.Error:
                                pass  # Ignore duplicate/constraint errors
        
        conn.commit()
        print(f"    Added {moves_added} moves from pre-evolutions")

    def _get_evolution_chain_for_pokemon(self, cursor, pokemon_id: int) -> List[int]:
        """Get full evolution chain for a Pokemon"""
        chain = []
        visited = set()
        
        def find_pre_evolutions(current_id: int):
            if current_id in visited:
                return
            visited.add(current_id)
            
            cursor.execute("""
                SELECT from_pokemon_id FROM Evolution 
                WHERE to_pokemon_id = ?
            """, (current_id,))
            
            pre_evolutions = cursor.fetchall()
            for (pre_evo_id,) in pre_evolutions:
                find_pre_evolutions(pre_evo_id)
                if pre_evo_id not in chain:
                    chain.append(pre_evo_id)
            
            if current_id not in chain:
                chain.append(current_id)
        
        find_pre_evolutions(pokemon_id)
        return chain

    def verify_database(self):
        """Verify the database setup is correct"""
        print("\n✅ Verifying database setup...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check Pokemon count
            cursor.execute("SELECT COUNT(*) FROM Pokemon")
            pokemon_count = cursor.fetchone()[0]
            print(f"  Pokemon entries: {pokemon_count}")
            
            # Check moves count
            cursor.execute("SELECT COUNT(*) FROM Moves")
            moves_count = cursor.fetchone()[0]
            print(f"  Moves entries: {moves_count}")
            
            # Check Pokemon-Moves relationships
            cursor.execute("SELECT COUNT(*) FROM PokemonMoves")
            pokemon_moves_count = cursor.fetchone()[0]
            print(f"  Pokemon-Moves relationships: {pokemon_moves_count}")
            
            # Check evolution relationships
            cursor.execute("SELECT COUNT(*) FROM Evolution")
            evolution_count = cursor.fetchone()[0]
            print(f"  Evolution relationships: {evolution_count}")
            
            # Sample some data
            print("\n📋 Sample data:")
            
            # Sample Pokemon
            cursor.execute("SELECT name, type1, type2 FROM Pokemon LIMIT 5")
            for name, type1, type2 in cursor.fetchall():
                types = f"{type1}/{type2}" if type2 else type1
                print(f"  Pokemon: {name} ({types})")
            
            # Sample evolutions
            cursor.execute("""
                SELECT p1.name, p2.name, e.evolution_method 
                FROM Evolution e
                JOIN Pokemon p1 ON e.from_pokemon_id = p1.pokedex_number
                JOIN Pokemon p2 ON e.to_pokemon_id = p2.pokedex_number
                LIMIT 5
            """)
            for pre_evo, evolution, method in cursor.fetchall():
                print(f"  Evolution: {pre_evo} → {evolution} (via {method})")
            
            # Check Charizard's total moves (should include pre-evolution moves)
            cursor.execute("""
                SELECT COUNT(*) FROM PokemonMoves WHERE pokemon_id = 6
            """)
            charizard_moves = cursor.fetchone()[0]
            print(f"  Charizard total moves: {charizard_moves}")
            
        print("\n🎉 Database verification complete!")

    def create_sample_team(self):
        """Create a sample team for testing"""
        print("\n👥 Creating sample team...")
        
        with sqlite3.connect(self.db_path) as conn:
            # Create team
            conn.execute("INSERT INTO Team (name) VALUES (?)", ("Sample Team",))
            team_id = conn.lastrowid
            
            # Add sample Pokemon
            sample_pokemon = [
                (6, "Charizard", 50),    # Charizard
                (9, "Blastoise", 48),    # Blastoise
                (3, "Venusaur", 49),     # Venusaur
                (25, "Pikachu", 45),     # Pikachu
                (143, "Snorlax", 52),    # Snorlax
                (150, "Mewtwo", 70)      # Mewtwo
            ]
            
            for pokemon_id, nickname, level in sample_pokemon:
                conn.execute("""
                    INSERT INTO TeamPokemon 
                    (team_id, pokemon_id, nickname, level, iv_attack, iv_defense, iv_speed, iv_special)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (team_id, pokemon_id, nickname, level, 15, 15, 15, 15))  # Perfect IVs
            
            conn.commit()
            
        print(f"✅ Sample team created with ID: {team_id}")


def main():
    """Main setup function"""
    setup = PokemonDatabaseSetup()
    
    print("Pokemon Database Complete Setup")
    print("==============================")
    print()
    print("This will create a complete Pokemon database with:")
    print("- All Generation 1 Pokemon (1-151)")
    print("- All Generation 1 moves")
    print("- Pokemon-Move relationships")
    print("- Evolution system with inherited moves")
    print("- Sample team for testing")
    print()
    
    force_recreate = input("Recreate database from scratch? (y/N): ").lower() == 'y'
    
    try:
        # Complete database setup
        setup.setup_complete_database(force_recreate=force_recreate)
        
        # Create sample team
        create_sample = input("\nCreate sample team? (y/N): ").lower() == 'y'
        if create_sample:
            setup.create_sample_team()
        
        print("\n" + "="*60)
        print("🎉 Pokemon Database Setup Complete!")
        print("="*60)
        print()
        print("You can now:")
        print("- Run your Flask app: python app.py")
        print("- Access Pokemon data via API endpoints")
        print("- Create and manage teams")
        print("- Use evolution-aware move system")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
