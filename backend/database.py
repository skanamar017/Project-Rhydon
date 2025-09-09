import sqlite3
from typing import Optional, List
from pydantic import BaseModel
import os
import math
import random
from flask import Flask, request, jsonify

app = Flask(__name__)

class Team(BaseModel):
    id: Optional[int] = None
    name: str

class TeamPokemon(BaseModel):
    id: Optional[int] = None
    team_id: int
    pokemon_id: int
    nickname: Optional[str] = None
    level: int
    # Individual Values (IVs) - Generation 1 uses 0-15 range
    iv_attack: int = 0
    iv_defense: int = 0
    iv_speed: int = 0
    iv_special: int = 0
    # Effort Values (EVs) - Generation 1 uses 0-65535 range
    ev_hp: int = 0
    ev_attack: int = 0
    ev_defense: int = 0
    ev_speed: int = 0
    ev_special: int = 0
    current_hp: Optional[int] = None
    status: Optional[str] = 'Healthy'
    # Move slots (Generation 1 allows 4 moves max)
    move1_id: Optional[int] = None
    move2_id: Optional[int] = None
    move3_id: Optional[int] = None
    move4_id: Optional[int] = None

class PokemonStats(BaseModel):
    hp: int
    attack: int
    defense: int
    speed: int
    special: int

class Gen1StatCalculator:
    @staticmethod
    def calculate_hp_iv(attack_iv: int, defense_iv: int, speed_iv: int, special_iv: int) -> int:
        """Calculate HP IV from other IVs in Generation 1"""
        return ((attack_iv % 2) * 8 + (defense_iv % 2) * 4 + 
                (speed_iv % 2) * 2 + (special_iv % 2))
    
    @staticmethod
    def calculate_hp_stat(base_hp: int, level: int, hp_iv: int, hp_ev: int) -> int:
        """Calculate HP stat using Generation 1 formula"""
        return int(((base_hp + hp_iv + math.sqrt(hp_ev) / 8 + 50) * level / 50) + 10)
    
    @staticmethod
    def calculate_other_stat(base_stat: int, level: int, iv: int, ev: int) -> int:
        """Calculate Attack/Defense/Speed/Special stats using Generation 1 formula"""
        return int(((base_stat + iv + math.sqrt(ev) / 8) * level / 50) + 5)
    
    @staticmethod
    def calculate_all_stats(base_stats: dict, level: int, ivs: dict, evs: dict) -> PokemonStats:
        """Calculate all stats for a Pokémon using Generation 1 formulas"""
        # Calculate HP IV from other IVs
        hp_iv = Gen1StatCalculator.calculate_hp_iv(
            ivs['attack'], ivs['defense'], ivs['speed'], ivs['special']
        )
        
        # Calculate all stats
        hp = Gen1StatCalculator.calculate_hp_stat(
            base_stats['hp'], level, hp_iv, evs['hp']
        )
        attack = Gen1StatCalculator.calculate_other_stat(
            base_stats['attack'], level, ivs['attack'], evs['attack']
        )
        defense = Gen1StatCalculator.calculate_other_stat(
            base_stats['defense'], level, ivs['defense'], evs['defense']
        )
        speed = Gen1StatCalculator.calculate_other_stat(
            base_stats['speed'], level, ivs['speed'], evs['speed']
        )
        special = Gen1StatCalculator.calculate_other_stat(
            base_stats['special'], level, ivs['special'], evs['special']
        )
        
        return PokemonStats(
            hp=hp, attack=attack, defense=defense, speed=speed, special=special
        )
    
    @staticmethod
    def generate_random_ivs() -> dict:
        """Generate random IVs for a new Pokémon (0-15 range)"""
        return {
            'attack': random.randint(0, 15),
            'defense': random.randint(0, 15),
            'speed': random.randint(0, 15),
            'special': random.randint(0, 15)
        }

class PokemonDatabase:
    def __init__(self, db_path: str = "pokemon.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database using create 4.sql and insert 7.sql"""
        if not os.path.exists(self.db_path):
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                for sql_file in ["create.sql", "insert.sql"]:
                    with open(sql_file, "r") as f:
                        sql_script = f.read()
                    conn.executescript(sql_script)
                conn.commit()


    def create_team(self, team: Team) -> Team:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO Team (name) VALUES (?)",
                (team.name,)
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

    def get_all_teams(self) -> List[Team]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM Team")
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
        # Check if team would be left with 0 Pokemon after deletion (optional constraint)
        current_pokemon_count = self.get_team_pokemon_count(team_id)
        # Note: Allowing deletion of teams even if they have Pokemon, 
        # but you could add a constraint here if needed
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM Team WHERE id = ?", (team_id,))
            conn.execute("DELETE FROM TeamPokemon WHERE team_id = ?", (team_id,))
            deleted = conn.total_changes > 0
            conn.commit()
            return deleted

    def get_team_pokemon_count(self, team_id: int) -> int:
        """Get the number of Pokemon currently in a team"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM TeamPokemon WHERE team_id = ?", (team_id,))
            count = cursor.fetchone()[0]
            return count

    def create_team_pokemon(self, tp: TeamPokemon) -> TeamPokemon:
        """Create a new team pokemon with randomly generated IVs if not provided, and set current_hp and status."""
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
        '''
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM TeamPokemon WHERE team_id = ?", (team_id,))
            rows = cursor.fetchall()
            return [TeamPokemon(**dict(row)) for row in rows]
        '''
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM TeamPokemon WHERE id = ?", (tp_id,))
            row = cursor.fetchone()
            if row:
                return TeamPokemon(**dict(row))
            return None


    def get_all_team_pokemons(self) -> List[TeamPokemon]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM TeamPokemon")
            rows = cursor.fetchall()
            return [TeamPokemon(**dict(row)) for row in rows]
        
    def get_team_pokemons_by_team_id(self, team_id: int) -> List[dict]:
        """Get trainer pokemon with species data and calculated stats"""
        print(f"[DEBUG] Getting Pokemon for trainer {team_id}")
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT tp.*, p.name as pokemon_name, p.type1, p.type2,
                       p.base_hp, p.base_attack, p.base_defense, p.base_speed, p.base_special
                FROM TeamPokemon tp
                JOIN Pokemon p ON tp.pokemon_id = p.id
                WHERE tp.team_id = ?
            """, (team_id,))
            rows = cursor.fetchall()
            print(f"[DEBUG] Found {len(rows)} Pokemon for trainer {team_id}")
            
            result = []
            for row in rows:
                # Convert row to dict
                pokemon_data = dict(row)
                print(f"[DEBUG] Processing Pokemon: {pokemon_data}")
                
                # Calculate HP IV from other IVs (Gen 1 mechanic)
                hp_iv = Gen1StatCalculator.calculate_hp_iv(
                    pokemon_data['iv_attack'], pokemon_data['iv_defense'], 
                    pokemon_data['iv_speed'], pokemon_data['iv_special']
                )
                
                # Calculate actual stats
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
                
                # Calculate stats
                calculated_stats = Gen1StatCalculator.calculate_all_stats(
                    base_stats, pokemon_data['level'], ivs, evs
                )
                
                # Add calculated stats to the data
                pokemon_data['calculated_hp'] = calculated_stats.hp
                pokemon_data['calculated_attack'] = calculated_stats.attack
                pokemon_data['calculated_defense'] = calculated_stats.defense
                pokemon_data['calculated_speed'] = calculated_stats.speed
                pokemon_data['calculated_special'] = calculated_stats.special
                
                # Remove base stat fields (not needed in frontend)
                for key in ['base_hp', 'base_attack', 'base_defense', 'base_speed', 'base_special']:
                    pokemon_data.pop(key, None)
                
                result.append(pokemon_data)
                
            print(f"[DEBUG] Returning Pokemon data: {result}")
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
        # First, get the team_id for this Pokemon
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT team_id FROM TeamPokemon WHERE id = ?", (tp_id,))
            result = cursor.fetchone()
            if not result:
                return False  # Pokemon doesn't exist
            
            team_id = result[0]
            
            # Check if this would leave the team with no Pokemon
            current_pokemon_count = self.get_team_pokemon_count(team_id)
            if current_pokemon_count <= 1:
                raise ValueError("Cannot delete the last Pokemon from a team. Teams must have at least 1 Pokemon.")
            
            # Proceed with deletion
            conn.execute("DELETE FROM TeamPokemon WHERE id = ?", (tp_id,))
            deleted = conn.total_changes > 0
            conn.commit()
            return deleted

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

    def calculate_trainer_pokemon_stats(self, tp_id: int) -> Optional[PokemonStats]:
        """Calculate actual stats for a trainer's Pokémon"""
        # Get trainer pokemon data
        tp = self.get_team_pokemon(tp_id)
        if not tp:
            return None
            
        # Get base stats
        base_stats = self.get_pokemon_base_stats(tp.pokemon_id)
        if not base_stats:
            return None
            
        # Prepare IVs and EVs dictionaries
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
        
        # Calculate and return stats
        return Gen1StatCalculator.calculate_all_stats(base_stats, tp.level, ivs, evs)

    def get_team_pokemon_with_stats(self, tp_id: int) -> Optional[dict]:
        """Get trainer pokemon data with calculated stats"""
        tp = self.get_team_pokemon(tp_id)
        if not tp:
            return None
            
        stats = self.calculate_trainer_pokemon_stats(tp_id)
        if not stats:
            return None
            
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

    def get_pokemon_moves_by_level(self, pokemon_id: int) -> dict:
        """Get all moves a Pokemon learns grouped by level"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT DISTINCT pm.move_id, m.name, m.type, m.power, m.accuracy, 
                       m.pp, pm.level_learned, m.effect
                FROM PokemonMoves pm
                JOIN Moves m ON pm.move_id = m.id
                WHERE pm.pokemon_id = ?
                ORDER BY pm.level_learned, m.name
            """, (pokemon_id,))
            
            moves_by_level = {}
            for row in cursor.fetchall():
                level = row['level_learned']
                if level not in moves_by_level:
                    moves_by_level[level] = []
                
                moves_by_level[level].append({
                    'move_id': row['move_id'],
                    'name': row['name'],
                    'type': row['type'],
                    'power': row['power'],
                    'accuracy': row['accuracy'],
                    'pp': row['pp'],
                    'effect_description': row['effect']
                })
            return moves_by_level

    def validate_pokemon_moves(self, pokemon_id: int, level: int, move_ids: List[int]) -> dict:
        """Validate that a Pokemon can learn the specified moves at their current level"""
        if len(move_ids) > 4:
            return {"valid": False, "errors": ["Pokemon can only have 4 moves maximum"]}
        
        # Remove None values and duplicates
        move_ids = list(set([mid for mid in move_ids if mid is not None]))
        
        available_moves = self.get_pokemon_available_moves(pokemon_id, level)
        available_move_ids = {move['move_id'] for move in available_moves}
        
        errors = []
        for move_id in move_ids:
            if move_id not in available_move_ids:
                move_name = self.get_move_name(move_id)
                errors.append(f"Pokemon cannot learn {move_name} at level {level}")
        
        return {"valid": len(errors) == 0, "errors": errors}

    def get_move_name(self, move_id: int) -> str:
        """Get move name by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT name FROM Moves WHERE id = ?", (move_id,))
            result = cursor.fetchone()
            return result[0] if result else f"Move #{move_id}"

    def update_team_pokemon_moves(self, tp_id: int, move_ids: List[int]) -> Optional[TeamPokemon]:
        """Update moves for a TeamPokemon"""
        # Pad move_ids to have exactly 4 elements (with None for empty slots)
        while len(move_ids) < 4:
            move_ids.append(None)
        move_ids = move_ids[:4]  # Ensure max 4 moves
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE TeamPokemon 
                SET move1_id = ?, move2_id = ?, move3_id = ?, move4_id = ?
                WHERE id = ?
            """, (move_ids[0], move_ids[1], move_ids[2], move_ids[3], tp_id))
            conn.commit()
        
        return self.get_team_pokemon(tp_id)

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