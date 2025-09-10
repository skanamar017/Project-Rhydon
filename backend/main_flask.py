# Combined Team and Pokémon info endpoint

from flask import Flask, request, jsonify, make_response
from database import PokemonDatabase, Team, TeamPokemon, Gen1StatCalculator
from typing import List
import json
import sqlite3
from flask_cors import CORS
import requests
import time
import os
import subprocess

app = Flask(__name__)

# Simple CORS configuration - REMOVE the complex one
CORS(app)

db = PokemonDatabase()

@app.route("/", methods=["GET"])
def home():
    return {"message": "Pokemon Team API"}

# Team Endpoints
@app.route("/Teams/", methods=["POST"])
def create_team():
    data = request.get_json()
    team = Team(**data)
    try:
        created = db.create_team(team)
        return jsonify(created.model_dump()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/Teams/<int:team_id>", methods=["GET"])
def get_team(team_id):
    trainer = db.get_team(team_id)
    if trainer:
        return jsonify(trainer.model_dump()), 200
    return jsonify({"error": "Team not found"}), 404

@app.route("/Teams/", methods=["GET"])
def get_all_teams():
    teams = db.get_all_teams()
    return jsonify([t.model_dump() for t in teams]), 200

@app.route("/Teams/<int:team_id>", methods=["PUT"])
def update_team(team_id):
    data = request.get_json()
    trainer = Team(**data)
    updated = db.update_team(team_id, trainer)
    if updated:
        return jsonify(updated.model_dump()), 200
    return jsonify({"error": "Team not found"}), 404

@app.route("/Teams/<int:team_id>", methods=["DELETE"])
def delete_team(team_id):
    if db.delete_team(team_id):
        return jsonify({"message": "Team deleted successfully"}), 200
    return jsonify({"error": "Team not found"}), 404

# TeamPokemon Endpoints
@app.route("/Teams/<int:team_id>/TeamPokemon/", methods=["POST"])
def create_team_pokemon(team_id):
    try:
        data = request.get_json()
        print(f"[DEBUG] Creating Pokemon for trainer {team_id} with data: {data}")
        
        # Ensure team_id is set in the data
        data['team_id'] = team_id
        
        # Validate Effort Values (EVs) - Generation 1 uses 0-65535 range (IVs are set when Pokemon is caught)
        ev_fields = ['ev_hp', 'ev_attack', 'ev_defense', 'ev_speed', 'ev_special']
        for ev_field in ev_fields:
            if ev_field in data:
                ev_value = data[ev_field]
                if not isinstance(ev_value, int) or ev_value < 0 or ev_value > 65535:
                    return jsonify({"error": f"{ev_field} must be between 0 and 65535"}), 400
        
        # Create TeamPokemon object
        tp = TeamPokemon(**data)
        created = db.create_team_pokemon(tp)
        
        print(f"[DEBUG] Successfully created Pokemon: {created}")
        return jsonify(created.model_dump()), 201
    except ValueError as ve:
        # Handle validation errors (like team size limits)
        print(f"[ERROR] Validation error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print(f"[ERROR] Failed to create Pokemon: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/Teams/<int:team_id>/TeamPokemon/<int:tp_id>", methods=["GET"])
def get_team_pokemon(team_id, tp_id):
    tp = db.get_team_pokemon(tp_id)
    if tp:
        return jsonify(tp.model_dump()), 200
    return jsonify({"error": "TeamPokemon not found"}), 404

@app.route("/Teams/<int:team_id>/TeamPokemon/<int:tp_id>/stats", methods=["GET"])
def get_team_pokemon_stats_route(team_id, tp_id):
    """Get calculated stats for a trainer's Pokémon"""
    details = db.get_team_pokemon_with_stats(tp_id)
    if details:
        return jsonify(details), 200
    return jsonify({"error": "Team Pokémon not found"}), 404

@app.route("/Teams/<int:team_id>/TeamPokemon/", methods=["GET"])
@app.route("/Teams/<int:team_id>/TeamPokemon", methods=["GET"])
def get_team_pokemons(team_id):
    print(f"[DEBUG] get_team_pokemons called for team_id={team_id}")
    tps = db.get_team_pokemons_by_team_id(team_id)
    # Since tps is now a List[dict], we don't need .model_dump()
    return jsonify(tps), 200

@app.route("/Teams/<int:team_id>/TeamPokemon/count", methods=["GET"])
def get_team_pokemon_count(team_id):
    """Get the current number of Pokemon in a team"""
    try:
        count = db.get_team_pokemon_count(team_id)
        return jsonify({
            "team_id": team_id,
            "pokemon_count": count,
            "can_add_more": count < 6,
            "can_remove": count > 1
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/Teams/<int:team_id>/TeamPokemon/<int:tp_id>", methods=["PUT"])
def update_team_pokemon(team_id, tp_id):
    try:
        data = request.get_json()
        print(f"[DEBUG] Updating Pokemon {tp_id} with data: {data}")
        
        # Get the existing trainer pokemon first
        existing_tp = db.get_team_pokemon(tp_id)
        if not existing_tp:
            return jsonify({"error": "TeamPokemon not found"}), 404
        
        # Update only the fields that are provided
        update_data = existing_tp.model_dump()
        
        # Basic fields
        if 'nickname' in data:
            update_data['nickname'] = data['nickname']
        if 'level' in data:
            update_data['level'] = data['level']
        if 'status' in data:
            update_data['status'] = data['status']
        if 'current_hp' in data:
            update_data['current_hp'] = data['current_hp']
        
        # Effort Values (EVs) - validate range 0-65535 (only EVs are editable, not IVs)
        ev_fields = ['ev_hp', 'ev_attack', 'ev_defense', 'ev_speed', 'ev_special']
        for ev_field in ev_fields:
            if ev_field in data:
                ev_value = data[ev_field]
                if not isinstance(ev_value, int) or ev_value < 0 or ev_value > 65535:
                    return jsonify({"error": f"{ev_field} must be between 0 and 65535"}), 400
                update_data[ev_field] = ev_value
        
        # Move slots
        move_fields = ['move1_id', 'move2_id', 'move3_id', 'move4_id']
        for move_field in move_fields:
            if move_field in data:
                update_data[move_field] = data[move_field]
        
        # Create updated TeamPokemon object with all required fields
        tp = TeamPokemon(**update_data)
        updated = db.update_team_pokemon(tp_id, tp)
        
        if updated:
            print(f"[DEBUG] Successfully updated Pokemon: {updated}")
            return jsonify(updated.model_dump()), 200
        else:
            return jsonify({"error": "Failed to update TeamPokemon"}), 500
            
    except Exception as e:
        print(f"[ERROR] Failed to update Pokemon: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/Teams/<int:team_id>/TeamPokemon/<int:tp_id>", methods=["DELETE"])
def delete_team_pokemon(team_id, tp_id):
    try:
        if db.delete_team_pokemon(tp_id):
            return jsonify({"message": "TeamPokemon deleted successfully"}), 200
        return jsonify({"error": "TeamPokemon not found"}), 404
    except ValueError as ve:
        # Handle validation errors (like trying to delete last Pokemon)
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/Pokemon/", methods=["GET"])
def get_all_pokemon():
    # Optional: filter by query param, e.g., ?type=Fire
    poke_type = request.args.get("type")
    with sqlite3.connect("pokemon.db") as conn:
        conn.row_factory = sqlite3.Row
        if poke_type:
            cursor = conn.execute("SELECT * FROM Pokemon WHERE type1 = ? OR type2 = ?", (poke_type, poke_type))
        else:
            cursor = conn.execute("SELECT * FROM Pokemon")
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
    return jsonify(result), 200

@app.route("/Pokemon/<int:pokemon_id>/moves", methods=["GET"])
def get_pokemon_moves(pokemon_id):
    """Get all moves for a specific Pokemon, optionally filtered by max level."""
    max_level = request.args.get("max_level", type=int)
    move_type = request.args.get("type")  # level-up, tm-hm, or all
    
    with sqlite3.connect("pokemon.db") as conn:
        conn.row_factory = sqlite3.Row
        
        # Base query
        query = """
        SELECT 
            pm.move_id,
            m.name as move_name,
            pm.level_learned,
            m.type as move_type,
            m.power,
            m.accuracy,
            m.pp,
            CASE 
                WHEN pm.level_learned = 0 THEN 'TM/HM'
                ELSE 'Level-up'
            END as learn_method
        FROM PokemonMoves pm
        JOIN Moves m ON pm.move_id = m.id
        WHERE pm.pokemon_id = ?
        """
        
        params = [pokemon_id]
        
        # Add filters
        if max_level is not None:
            query += " AND (pm.level_learned <= ? OR pm.level_learned = 0)"
            params.append(max_level)
        
        if move_type == "level-up":
            query += " AND pm.level_learned > 0"
        elif move_type == "tm-hm":
            query += " AND pm.level_learned = 0"
        
        query += " ORDER BY pm.level_learned, m.name"
        
        cursor = conn.execute(query, params)
        moves = cursor.fetchall()
        
        # Get Pokemon name for response
        pokemon_cursor = conn.execute("SELECT name FROM Pokemon WHERE id = ?", [pokemon_id])
        pokemon_result = pokemon_cursor.fetchone()
        pokemon_name = pokemon_result[0] if pokemon_result else f"Pokemon #{pokemon_id}"
        
        result = {
            "pokemon_id": pokemon_id,
            "pokemon_name": pokemon_name,
            "filters": {
                "max_level": max_level,
                "type": move_type
            },
            "moves": [dict(move) for move in moves]
        }
        
        return jsonify(result), 200

@app.route("/Pokemon/<int:pokemon_id>/moves/level/<int:level>", methods=["GET"])
def get_pokemon_moves_at_level(pokemon_id, level):
    """Get moves that a Pokemon learns at a specific level."""
    with sqlite3.connect("pokemon.db") as conn:
        conn.row_factory = sqlite3.Row
        
        query = """
        SELECT 
            pm.move_id,
            m.name as move_name,
            pm.level_learned,
            m.type as move_type,
            m.power,
            m.accuracy,
            m.pp
        FROM PokemonMoves pm
        JOIN Moves m ON pm.move_id = m.id
        WHERE pm.pokemon_id = ? AND pm.level_learned = ?
        ORDER BY m.name
        """
        
        cursor = conn.execute(query, [pokemon_id, level])
        moves = cursor.fetchall()
        
        # Get Pokemon name
        pokemon_cursor = conn.execute("SELECT name FROM Pokemon WHERE id = ?", [pokemon_id])
        pokemon_result = pokemon_cursor.fetchone()
        pokemon_name = pokemon_result[0] if pokemon_result else f"Pokemon #{pokemon_id}"
        
        result = {
            "pokemon_id": pokemon_id,
            "pokemon_name": pokemon_name,
            "level": level,
            "moves": [dict(move) for move in moves]
        }
        
        return jsonify(result), 200

@app.route("/Pokemon/<int:pokemon_id>/moves/with_evolutions", methods=["GET"])
def get_pokemon_moves_with_evolutions(pokemon_id):
    """Get all moves for a Pokemon including those learned from previous evolutions."""
    max_level = request.args.get("max_level", type=int)
    move_type = request.args.get("type")  # level-up, tm-hm, or all
    
    with sqlite3.connect("pokemon.db") as conn:
        conn.row_factory = sqlite3.Row
        
        # Get evolution chain for this Pokemon
        def get_evolution_chain(current_id: int) -> List[int]:
            """Get all pre-evolutions and current Pokemon"""
            chain = []
            visited = set()
            
            def find_pre_evolutions(curr_id: int):
                if curr_id in visited:
                    return
                visited.add(curr_id)
                
                # Find what this Pokemon evolves from
                cursor = conn.execute("""
                    SELECT from_pokemon_id FROM Evolution 
                    WHERE to_pokemon_id = ?
                """, (curr_id,))
                
                pre_evolutions = cursor.fetchall()
                for (pre_evo_id,) in pre_evolutions:
                    find_pre_evolutions(pre_evo_id)
                    if pre_evo_id not in chain:
                        chain.append(pre_evo_id)
                
                if curr_id not in chain:
                    chain.append(curr_id)
            
            find_pre_evolutions(current_id)
            return chain
        
        # Get full evolution chain
        evolution_chain = get_evolution_chain(pokemon_id)
        
        # Base query for moves from entire evolution chain
        query = """
        SELECT DISTINCT
            pm.move_id,
            m.name as move_name,
            pm.level_learned,
            m.type as move_type,
            m.power,
            m.accuracy,
            m.pp,
            p.name as learned_from_pokemon,
            p.pokedex_number as learned_from_id,
            CASE 
                WHEN pm.level_learned = 0 THEN 'TM/HM'
                ELSE 'Level-up'
            END as learn_method
        FROM PokemonMoves pm
        JOIN Moves m ON pm.move_id = m.id
        JOIN Pokemon p ON pm.pokemon_id = p.pokedex_number
        WHERE pm.pokemon_id IN ({})
        """.format(','.join(['?'] * len(evolution_chain)))
        
        params = evolution_chain[:]
        
        # Add filters
        if max_level is not None:
            query += " AND (pm.level_learned <= ? OR pm.level_learned = 0)"
            params.append(max_level)
        
        if move_type == "level-up":
            query += " AND pm.level_learned > 0"
        elif move_type == "tm-hm":
            query += " AND pm.level_learned = 0"
        
        query += " ORDER BY pm.level_learned, m.name"
        
        cursor = conn.execute(query, params)
        moves = cursor.fetchall()
        
        # Get Pokemon name for response
        pokemon_cursor = conn.execute("SELECT name FROM Pokemon WHERE pokedex_number = ?", [pokemon_id])
        pokemon_result = pokemon_cursor.fetchone()
        pokemon_name = pokemon_result[0] if pokemon_result else f"Pokemon #{pokemon_id}"
        
        # Get evolution chain names
        chain_names = {}
        for evo_id in evolution_chain:
            cursor = conn.execute("SELECT name FROM Pokemon WHERE pokedex_number = ?", [evo_id])
            result = cursor.fetchone()
            if result:
                chain_names[evo_id] = result[0]
        
        result = {
            "pokemon_id": pokemon_id,
            "pokemon_name": pokemon_name,
            "evolution_chain": [{"id": evo_id, "name": chain_names.get(evo_id, f"Pokemon #{evo_id}")} 
                              for evo_id in evolution_chain],
            "filters": {
                "max_level": max_level,
                "type": move_type
            },
            "total_moves": len(moves),
            "moves": [dict(move) for move in moves]
        }
        
        return jsonify(result), 200

@app.route("/pokemon/<int:pokemon_id>/base_stats", methods=["GET"])
def get_pokemon_base_stats_route(pokemon_id: int):
    """Get base stats for a Pokémon species"""
    base_stats = db.get_pokemon_base_stats(pokemon_id)
    if base_stats:
        return jsonify(base_stats), 200
    return jsonify({"error": "Pokémon not found"}), 404

@app.route("/calculate_stats", methods=["POST"])
def calculate_stats_endpoint():
    """Calculate stats given base stats, level, IVs, and EVs"""
    data = request.get_json()
    required_fields = ['base_stats', 'level', 'ivs', 'evs']
    
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": "Required fields: base_stats, level, ivs, evs"}), 400
    
    try:
        stats = Gen1StatCalculator.calculate_all_stats(
            data['base_stats'], data['level'], data['ivs'], data['evs']
        )
        return jsonify(stats.dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Move Management Endpoints
@app.route("/pokemon/<int:pokemon_id>/available_moves", methods=["GET"])
def get_available_moves(pokemon_id: int):
    """Get all moves a Pokémon can learn up to a specific level"""
    level = request.args.get('level', type=int)
    if not level:
        return jsonify({"error": "Level parameter is required"}), 400
    
    try:
        moves = db.get_pokemon_available_moves(pokemon_id, level)
        return jsonify(moves), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/pokemon/<int:pokemon_id>/moves_by_level", methods=["GET"])
def get_moves_by_level(pokemon_id: int):
    """Get all moves a Pokémon learns grouped by level"""
    try:
        moves = db.get_pokemon_moves_by_level(pokemon_id)
        return jsonify(moves), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/Teams/<int:team_id>/TeamPokemon/<int:tp_id>/moves", methods=["PUT"])
def update_pokemon_moves(team_id: int, tp_id: int):
    """Update moves for a TeamPokemon, with level validation"""
    data = request.get_json()
    
    try:
        # Get current TeamPokemon to check level
        team_pokemon = db.get_team_pokemon(tp_id)
        if not team_pokemon:
            return jsonify({"error": "TeamPokemon not found"}), 404
            
        # Validate moves against Pokemon's level and movepool
        validation_result = db.validate_pokemon_moves(
            team_pokemon.pokemon_id, 
            team_pokemon.level, 
            data.get('move_ids', [])
        )
        
        if not validation_result["valid"]:
            return jsonify({
                "error": "Invalid moves", 
                "details": validation_result["errors"]
            }), 400
        
        # Update moves
        updated = db.update_team_pokemon_moves(tp_id, data.get('move_ids', []))
        if updated:
            return jsonify(updated.model_dump()), 200
        else:
            return jsonify({"error": "Failed to update moves"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/moves/<int:move_id>", methods=["GET"])
def get_move_details(move_id: int):
    """Get detailed information about a move"""
    try:
        move = db.get_move_details(move_id)
        if move:
            return jsonify(move), 200
        return jsonify({"error": "Move not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/Teams/<int:team_id>/TeamPokemon/<int:tp_id>/stats", methods=["PUT"])
def update_pokemon_stats(team_id: int, tp_id: int):
    """Update Pokemon EVs and IVs"""
    try:
        data = request.get_json()
        print(f"[DEBUG] Updating stats for Pokemon {tp_id} with data: {data}")
        
        # Get the existing trainer pokemon first
        existing_tp = db.get_team_pokemon(tp_id)
        if not existing_tp:
            return jsonify({"error": "TeamPokemon not found"}), 404
        
        update_data = existing_tp.model_dump()
        
        # Validate and update Individual Values (IVs) - Generation 1 uses 0-15 range
        if 'ivs' in data:
            ivs = data['ivs']
            iv_fields = ['attack', 'defense', 'speed', 'special']
            for iv_field in iv_fields:
                if iv_field in ivs:
                    iv_value = ivs[iv_field]
                    if not isinstance(iv_value, int) or iv_value < 0 or iv_value > 15:
                        return jsonify({"error": f"IV {iv_field} must be between 0 and 15"}), 400
                    update_data[f'iv_{iv_field}'] = iv_value
        
        # Validate and update Effort Values (EVs) - Generation 1 uses 0-65535 range
        if 'evs' in data:
            evs = data['evs']
            ev_fields = ['hp', 'attack', 'defense', 'speed', 'special']
            for ev_field in ev_fields:
                if ev_field in evs:
                    ev_value = evs[ev_field]
                    if not isinstance(ev_value, int) or ev_value < 0 or ev_value > 65535:
                        return jsonify({"error": f"EV {ev_field} must be between 0 and 65535"}), 400
                    update_data[f'ev_{ev_field}'] = ev_value
        
        # Create updated TeamPokemon object
        tp = TeamPokemon(**update_data)
        updated = db.update_team_pokemon(tp_id, tp)
        
        if updated:
            print(f"[DEBUG] Successfully updated Pokemon stats: {updated}")
            return jsonify({
                "message": "Pokemon stats updated successfully",
                "pokemon": updated.model_dump()
            }), 200
        else:
            return jsonify({"error": "Failed to update Pokemon stats"}), 500
            
    except Exception as e:
        print(f"[ERROR] Failed to update Pokemon stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/Teams/<int:team_id>/TeamPokemon/<int:tp_id>/stats", methods=["GET"])
def get_pokemon_stats(team_id: int, tp_id: int):
    """Get Pokemon EVs and IVs in a structured format"""
    try:
        tp = db.get_team_pokemon(tp_id)
        if not tp:
            return jsonify({"error": "TeamPokemon not found"}), 404
        
        stats_data = {
            "ivs": {
                "attack": tp.iv_attack,
                "defense": tp.iv_defense,
                "speed": tp.iv_speed,
                "special": tp.iv_special
            },
            "evs": {
                "hp": tp.ev_hp,
                "attack": tp.ev_attack,
                "defense": tp.ev_defense,
                "speed": tp.ev_speed,
                "special": tp.ev_special
            },
            "level": tp.level,
            "nickname": tp.nickname,
            "pokemon_id": tp.pokemon_id
        }
        
        return jsonify(stats_data), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to get Pokemon stats: {str(e)}")
        return jsonify({"error": str(e)}), 500

def setup_evolution_system():
    """Automatically set up the evolution system if it doesn't exist"""
    try:
        print("🔍 Checking evolution system status...")
        
        # Check if Evolution table exists and has data
        conn = sqlite3.connect("pokemon.db")
        cursor = conn.cursor()
        
        # Check if Evolution table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='Evolution'
        """)
        
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print("❌ Evolution table not found")
            print("🚀 Setting up evolution system automatically...")
            conn.close()
            
            # Run the external setup script
            import subprocess
            result = subprocess.run(["python", "setup_evolution_system.py"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Evolution system setup completed!")
            else:
                print(f"❌ Setup failed: {result.stderr}")
            return True
        
        # Check if table has data
        cursor.execute("SELECT COUNT(*) FROM Evolution")
        evolution_count = cursor.fetchone()[0]
        
        if evolution_count == 0:
            print("❌ Evolution table is empty")
            print("🚀 Setting up evolution system automatically...")
            conn.close()
            
            # Run the external setup script
            import subprocess
            result = subprocess.run(["python", "setup_evolution_system.py"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Evolution system setup completed!")
            else:
                print(f"❌ Setup failed: {result.stderr}")
            return True
        
        # Check if PokemonMoves has evolution moves (rough estimate)
        cursor.execute("SELECT COUNT(*) FROM PokemonMoves")
        total_moves = cursor.fetchone()[0]
        
        conn.close()
        
        if total_moves < 4100:  # Should be around 4172 with evolution moves
            print(f"⚠️  PokemonMoves count ({total_moves}) suggests missing evolution moves")
            print("🚀 Updating Pokemon moves with evolution data...")
            
            # Run the external setup script
            import subprocess
            result = subprocess.run(["python", "setup_evolution_system.py"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Evolution system setup completed!")
            else:
                print(f"❌ Setup failed: {result.stderr}")
            return True
        
        print(f"✅ Evolution system already set up ({evolution_count} evolutions, {total_moves} moves)")
        return False
        
    except Exception as e:
        print(f"❌ Error checking evolution system: {e}")
        return False

if __name__ == "__main__":
    # Automatically set up evolution system on startup
    setup_evolution_system()
    app.run(debug=True, port=5001)
