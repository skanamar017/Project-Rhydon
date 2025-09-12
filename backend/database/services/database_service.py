"""
Database service layer for Pokemon team management.
Handles all database operations without Flask dependencies.
"""

import sqlite3
from typing import Optional, List
import os
from .models import Team, TeamPokemon, Gen1StatCalculator, User, hash_password, verify_password

class PokemonDatabase:
    # User Operations
    def register_user(self, username: str, plain_password: str) -> User:
        """Register a new user with hashed password. Returns User or raises if username exists."""
        password_hash = hash_password(plain_password)
        with sqlite3.connect(self.db_path) as conn:
            try:
                cursor = conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                user_id = cursor.lastrowid
                conn.commit()
                return User(id=user_id, username=username, password_hash=password_hash)
            except sqlite3.IntegrityError:
                raise ValueError("Username already exists")

    def authenticate_user(self, username: str, plain_password: str) -> User:
        """Authenticate user by username and password. Returns User if valid, else None."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row and verify_password(plain_password, row['password_hash']):
                return User(id=row['id'], username=row['username'], password_hash=row['password_hash'])
            return None

    def __init__(self, db_path: str = "pokemon.db"):
        # If db_path is just a filename, place it in the database directory
        if not os.path.dirname(db_path):
            service_dir = os.path.dirname(os.path.abspath(__file__))
            database_dir = os.path.dirname(service_dir)  # Go up one level to database/
            self.db_path = os.path.join(database_dir, db_path)
        else:
            self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database using create.sql and all insert files"""
        if not os.path.exists(self.db_path):
            # Get the directory where this service file is located
            service_dir = os.path.dirname(os.path.abspath(__file__))
            database_dir = os.path.dirname(service_dir)  # Go up one level to database/
            
            with sqlite3.connect(self.db_path) as conn:
                # First create the tables
                create_sql_path = os.path.join(database_dir, "create.sql")
                with open(create_sql_path, "r") as f:
                    sql_script = f.read()
                conn.executescript(sql_script)
                
                # Temporarily disable foreign keys for data insertion
                conn.execute("PRAGMA foreign_keys = OFF")
                
                # Then insert data files individually to handle errors
                sql_files = [
                    "gen1_pokemon_inserts.sql",  # Pokemon data first
                    "gen1_moves_inserts.sql",    # Then moves
                    "gen1_pokemon_moves_inserts_corrected.sql"  # Then pokemon-move relationships
                ]
                
                for sql_file in sql_files:
                    sql_file_path = os.path.join(database_dir, "data", sql_file)
                    if os.path.exists(sql_file_path):
                        try:
                            with open(sql_file_path, "r") as f:
                                sql_script = f.read()
                            conn.executescript(sql_script)
                            print(f"Successfully loaded {sql_file}")
                        except Exception as e:
                            print(f"Warning: Could not load {sql_file}: {e}")
                                
                # Re-enable foreign keys
                conn.execute("PRAGMA foreign_keys = ON")
                conn.commit()

    # Team Operations
    def create_team(self, team: Team, user_id: int) -> Team:
        """Create a team for a specific user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO Team (name, user_id) VALUES (?, ?)",
                (team.name, user_id)
            )
            team.id = cursor.lastrowid
            conn.commit()
        return team

    def get_team(self, team_id: int) -> Optional[Team]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM Team WHERE id = ?", (team_id,))
            row = cursor.fetchone()
            if row:
                return Team(**dict(row))
        return None


    def get_teams_by_user(self, user_id: int) -> List[Team]:
        """Get all teams belonging to a specific user."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM Team WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            return [Team(**dict(row)) for row in rows]

    def update_team(self, team_id: int, team: Team) -> Optional[Team]:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE Team SET name = ? WHERE id = ?",
                (team.name, team_id)
            )
            if conn.total_changes == 0:
                return None
            conn.commit()
            team.id = team_id
            return team

    def delete_team(self, team_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM Team WHERE id = ?", (team_id,))
            conn.execute("DELETE FROM TeamPokemon WHERE team_id = ?", (team_id,))
            deleted = conn.total_changes > 0
            conn.commit()
            return deleted

    # TeamPokemon Operations
    def get_team_pokemon_count(self, team_id: int) -> int:
        """Get the number of Pokemon currently in a team"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM TeamPokemon WHERE team_id = ?", (team_id,))
            count = cursor.fetchone()[0]
            return count

    def create_team_pokemon(self, tp: TeamPokemon) -> TeamPokemon:
        """Create a new team pokemon with randomly generated IVs if not provided"""
        # Check if team already has 6 Pokemon
        current_pokemon_count = self.get_team_pokemon_count(tp.team_id)
        if current_pokemon_count >= 6:
            raise ValueError("Team cannot have more than 6 Pokemon")
        
        # Always generate random IVs if they're all 0 (default values)
        if (tp.iv_attack == 0 and tp.iv_defense == 0 and 
            tp.iv_speed == 0 and tp.iv_special == 0):
            random_ivs = Gen1StatCalculator.generate_random_ivs()
            tp.iv_attack = random_ivs['attack']
            tp.iv_defense = random_ivs['defense'] 
            tp.iv_speed = random_ivs['speed']
            tp.iv_special = random_ivs['special']

        # Calculate max HP for this Pokémon
        base_stats = self.get_pokemon_base_stats(tp.pokemon_id)
        if base_stats:
            hp_iv = Gen1StatCalculator.calculate_hp_iv(tp.iv_attack, tp.iv_defense, tp.iv_speed, tp.iv_special)
            max_hp = Gen1StatCalculator.calculate_hp_stat(base_stats['hp'], tp.level, hp_iv, tp.ev_hp)
        else:
            max_hp = 10  # fallback
        tp.current_hp = max_hp
        tp.status = tp.status or 'Healthy'

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """INSERT INTO TeamPokemon 
                   (team_id, pokemon_id, nickname, level,
                    iv_attack, iv_defense, iv_speed, iv_special,
                    ev_hp, ev_attack, ev_defense, ev_speed, ev_special,
                    current_hp, status, move1_id, move2_id, move3_id, move4_id) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (tp.team_id, tp.pokemon_id, tp.nickname, tp.level,
                 tp.iv_attack, tp.iv_defense, tp.iv_speed, tp.iv_special,
                 tp.ev_hp, tp.ev_attack, tp.ev_defense, tp.ev_speed, tp.ev_special,
                 tp.current_hp, tp.status, tp.move1_id, tp.move2_id, tp.move3_id, tp.move4_id)
            )
            tp.id = cursor.lastrowid
            conn.commit()
        return tp

    def get_team_pokemon(self, tp_id: int) -> Optional[TeamPokemon]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM TeamPokemon WHERE id = ?", (tp_id,))
            row = cursor.fetchone()
            if row:
                return TeamPokemon(**dict(row))
            return None

    def get_team_pokemons_by_team_id(self, team_id: int) -> List[dict]:
        """Get team pokemon with species data and calculated stats"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT tp.*, p.name as pokemon_name, p.type1, p.type2,
                       p.base_hp, p.base_attack, p.base_defense, p.base_speed, p.base_special
                FROM TeamPokemon tp
                JOIN Pokemon p ON tp.pokemon_id = p.pokedex_number
                WHERE tp.team_id = ?
            """, (team_id,))
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                pokemon_data = dict(row)
                
                # Calculate stats
                base_stats = {
                    'hp': pokemon_data['base_hp'],
                    'attack': pokemon_data['base_attack'],
                    'defense': pokemon_data['base_defense'],
                    'speed': pokemon_data['base_speed'],
                    'special': pokemon_data['base_special']
                }
                
                ivs = {
                    'attack': pokemon_data['iv_attack'],
                    'defense': pokemon_data['iv_defense'],
                    'speed': pokemon_data['iv_speed'],
                    'special': pokemon_data['iv_special']
                }
                
                evs = {
                    'hp': pokemon_data['ev_hp'],
                    'attack': pokemon_data['ev_attack'],
                    'defense': pokemon_data['ev_defense'],
                    'speed': pokemon_data['ev_speed'],
                    'special': pokemon_data['ev_special']
                }
                
                calculated_stats = Gen1StatCalculator.calculate_all_stats(
                    base_stats, pokemon_data['level'], ivs, evs
                )
                
                # Add calculated stats to the data
                pokemon_data['calculated_hp'] = calculated_stats.hp
                pokemon_data['calculated_attack'] = calculated_stats.attack
                pokemon_data['calculated_defense'] = calculated_stats.defense
                pokemon_data['calculated_speed'] = calculated_stats.speed
                pokemon_data['calculated_special'] = calculated_stats.special
                
                # Remove base stat fields
                for key in ['base_hp', 'base_attack', 'base_defense', 'base_speed', 'base_special']:
                    pokemon_data.pop(key, None)
                
                result.append(pokemon_data)
                
            return result

    def update_team_pokemon(self, tp_id: int, tp: TeamPokemon) -> Optional[TeamPokemon]:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE TeamPokemon 
                   SET team_id = ?, pokemon_id = ?, nickname = ?, level = ?,
                   iv_attack = ?, iv_defense = ?, iv_speed = ?, iv_special = ?,
                   ev_hp = ?, ev_attack = ?, ev_defense = ?, ev_speed = ?, ev_special = ?,
                   current_hp = ?, status = ?, move1_id = ?, move2_id = ?, move3_id = ?, move4_id = ?
               WHERE id = ?""",
                (tp.team_id, tp.pokemon_id, tp.nickname, tp.level,
                 tp.iv_attack, tp.iv_defense, tp.iv_speed, tp.iv_special,
                 tp.ev_hp, tp.ev_attack, tp.ev_defense, tp.ev_speed, tp.ev_special,
                 tp.current_hp, tp.status, tp.move1_id, tp.move2_id, tp.move3_id, tp.move4_id,
                 tp_id)
            )
            if conn.total_changes == 0:
                return None
            conn.commit()
            tp.id = tp_id
            return tp

    def delete_team_pokemon(self, tp_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT team_id FROM TeamPokemon WHERE id = ?", (tp_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            team_id = result[0]
            
            # Check if this would leave the team with no Pokemon
            current_pokemon_count = self.get_team_pokemon_count(team_id)
            if current_pokemon_count <= 1:
                raise ValueError("Cannot delete the last Pokemon from a team. Teams must have at least 1 Pokemon.")
            
            conn.execute("DELETE FROM TeamPokemon WHERE id = ?", (tp_id,))
            deleted = conn.total_changes > 0
            conn.commit()
            return deleted

    # Pokemon Base Data Operations
    def get_pokemon_base_stats(self, pokemon_id: int) -> Optional[dict]:
        """Get base stats for a Pokémon species"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT base_hp, base_attack, base_defense, base_special, base_speed FROM Pokemon WHERE id = ?", 
                (pokemon_id,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    'hp': row['base_hp'],
                    'attack': row['base_attack'], 
                    'defense': row['base_defense'],
                    'special': row['base_special'],
                    'speed': row['base_speed']
                }
            return None

    def get_team_pokemon_with_stats(self, tp_id: int) -> Optional[dict]:
        """Get team pokemon data with calculated stats"""
        tp = self.get_team_pokemon(tp_id)
        if not tp:
            return None
            
        # Calculate stats
        base_stats = self.get_pokemon_base_stats(tp.pokemon_id)
        if not base_stats:
            return None
            
        ivs = {
            'attack': tp.iv_attack,
            'defense': tp.iv_defense,
            'speed': tp.iv_speed,
            'special': tp.iv_special
        }
        
        evs = {
            'hp': tp.ev_hp,
            'attack': tp.ev_attack,
            'defense': tp.ev_defense,
            'speed': tp.ev_speed,
            'special': tp.ev_special
        }
        
        stats = Gen1StatCalculator.calculate_all_stats(base_stats, tp.level, ivs, evs)
        
        # Get Pokemon name and other details
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT name, pokedex_number, type1, type2 FROM Pokemon WHERE id = ?",
                (tp.pokemon_id,)
            )
            pokemon_row = cursor.fetchone()
            
        result = tp.dict()
        result['calculated_stats'] = stats.dict()
        if pokemon_row:
            result['pokemon_name'] = pokemon_row['name']
            result['pokedex_number'] = pokemon_row['pokedex_number']
            result['type1'] = pokemon_row['type1']
            result['type2'] = pokemon_row['type2']
            
        return result

    # Move Management Methods
    def get_pokemon_available_moves(self, pokemon_id: int, max_level: int) -> List[dict]:
        """Get all moves a Pokemon can learn up to a specific level"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT DISTINCT pm.move_id, m.name, m.type, m.power, m.accuracy, 
                       m.pp, pm.level_learned, m.effect
                FROM PokemonMoves pm
                JOIN Moves m ON pm.move_id = m.id
                WHERE pm.pokemon_id = ? AND pm.level_learned <= ?
                ORDER BY pm.level_learned, m.name
            """, (pokemon_id, max_level))
            
            moves = []
            for row in cursor.fetchall():
                moves.append({
                    'move_id': row['move_id'],
                    'name': row['name'],
                    'type': row['type'],
                    'power': row['power'],
                    'accuracy': row['accuracy'],
                    'pp': row['pp'],
                    'level_learned': row['level_learned'],
                    'effect_description': row['effect']
                })
            return moves

    def get_move_details(self, move_id: int) -> Optional[dict]:
        """Get detailed information about a move"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, name, type, power, accuracy, pp, effect
                FROM Moves WHERE id = ?
            """, (move_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'name': row['name'],
                    'type': row['type'],
                    'power': row['power'],
                    'accuracy': row['accuracy'],
                    'pp': row['pp'],
                    'effect_description': row['effect']
                }
            return None
