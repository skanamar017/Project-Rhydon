#!/usr/bin/env python3
"""
Calculate correct HP values for all TrainerPokemon using Generation 1 formulas
"""

import sqlite3
from database import Gen1StatCalculator

def get_pokemon_base_hp(conn, pokemon_id):
    """Get base HP stat for a Pokemon"""
    cursor = conn.execute("SELECT hp FROM Pokemon WHERE id = ?", [pokemon_id])
    result = cursor.fetchone()
    return result[0] if result else 35  # fallback

def calculate_correct_hp_values():
    """Calculate and display correct HP values for all TrainerPokemon"""
    
    conn = sqlite3.connect("pokemon.db")
    conn.row_factory = sqlite3.Row
    
    # Get all TrainerPokemon
    cursor = conn.execute("""
        SELECT tp.*, p.name as pokemon_name, p.base_hp
        FROM TrainerPokemon tp
        JOIN Pokemon p ON tp.pokemon_id = p.id
        ORDER BY tp.id
    """)
    
    trainer_pokemon = cursor.fetchall()
    
    print("TrainerPokemon HP Analysis")
    print("=" * 80)
    print(f"{'ID':<3} {'Pokemon':<12} {'Nickname':<12} {'Lvl':<3} {'IVs (A/D/S/Sp)':<14} {'Base HP':<7} {'Calc HP':<7} {'Current':<7} {'Match':<5}")
    print("-" * 80)
    
    for tp in trainer_pokemon:
        # Calculate HP IV from other IVs
        hp_iv = Gen1StatCalculator.calculate_hp_iv(
            tp['iv_attack'], tp['iv_defense'], tp['iv_speed'], tp['iv_special']
        )
        
        # Calculate correct HP
        calculated_hp = Gen1StatCalculator.calculate_hp_stat(
            tp['base_hp'], tp['level'], hp_iv, tp['ev_hp']
        )
        
        # Check if it matches current value
        matches = "✓" if calculated_hp == tp['current_hp'] else "✗"
        
        ivs_str = f"{tp['iv_attack']}/{tp['iv_defense']}/{tp['iv_speed']}/{tp['iv_special']}"
        
        print(f"{tp['id']:<3} {tp['pokemon_name']:<12} {tp['nickname']:<12} {tp['level']:<3} {ivs_str:<14} {tp['base_hp']:<7} {calculated_hp:<7} {tp['current_hp']:<7} {matches:<5}")
    
    conn.close()

if __name__ == "__main__":
    calculate_correct_hp_values()
