"""
Pydantic models for Pokemon team management system.
Separated from database logic for better organization.
"""

from typing import Optional
from pydantic import BaseModel
import random
import math
import bcrypt


def hash_password(plain_password: str) -> str:
    """Hash a password for storing."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


class User(BaseModel):
    id: Optional[int] = None
    username: str
    password_hash: str

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
    """Generation 1 Pokemon stat calculation utilities"""
    
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
