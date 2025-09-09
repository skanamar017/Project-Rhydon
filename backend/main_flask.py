# Combined Team and Pokémon info endpoint

from flask import Flask, request, jsonify, make_response
from database import PokemonDatabase, Team, TeamPokemon, Gen1StatCalculator
from typing import List
import json
import sqlite3
from flask_cors import CORS

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
        if 'nickname' in data:
            update_data['nickname'] = data['nickname']
        if 'level' in data:
            update_data['level'] = data['level']
        
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

if __name__ == "__main__":
    app.run(debug=True, port=5001)
