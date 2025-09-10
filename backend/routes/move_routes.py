"""
Flask route handlers for move management endpoints.
"""

from flask import Blueprint, request, jsonify
import sqlite3
from move_service import MoveService
from models import Gen1StatCalculator

move_bp = Blueprint('moves', __name__)

@move_bp.route("/Pokemon/", methods=["GET"])
def get_all_pokemon():
    """Get all Pokemon with optional type filtering"""
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

@move_bp.route("/Pokemon/<int:pokemon_id>/moves", methods=["GET"])
def get_pokemon_moves(pokemon_id):
    """Get all moves for a specific Pokemon, optionally filtered by max level."""
    move_service = MoveService()
    max_level = request.args.get("max_level", type=int)
    move_type = request.args.get("type")
    
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
        
        # Get Pokemon name
        pokemon_cursor = conn.execute("SELECT name FROM Pokemon WHERE id = ?", [pokemon_id])
        pokemon_result = pokemon_cursor.fetchone()
        pokemon_name = pokemon_result[0] if pokemon_result else f"Pokemon #{pokemon_id}"
        
        result = {
            "pokemon_id": pokemon_id,
            "pokemon_name": pokemon_name,
            "filters": {"max_level": max_level, "type": move_type},
            "moves": [dict(move) for move in moves]
        }
        
        return jsonify(result), 200

@move_bp.route("/Pokemon/<int:pokemon_id>/moves/with_evolutions", methods=["GET"])
def get_pokemon_moves_with_evolutions(pokemon_id):
    """Get all moves for a Pokemon including those from previous evolutions."""
    move_service = MoveService()
    result = move_service.get_pokemon_moves_with_evolutions(pokemon_id)
    
    # Apply filters if provided
    max_level = request.args.get("max_level", type=int)
    move_type = request.args.get("type")
    
    if max_level is not None or move_type:
        filtered_moves = []
        for move in result["moves"]:
            # Apply level filter
            if max_level is not None:
                if move["level_learned"] > max_level and move["level_learned"] != 0:
                    continue
            
            # Apply type filter
            if move_type == "level-up" and move["level_learned"] == 0:
                continue
            elif move_type == "tm-hm" and move["level_learned"] != 0:
                continue
            
            filtered_moves.append(move)
        
        result["moves"] = filtered_moves
        result["total_moves"] = len(filtered_moves)
    
    result["filters"] = {"max_level": max_level, "type": move_type}
    return jsonify(result), 200

@move_bp.route("/Pokemon/<int:pokemon_id>/moves/level/<int:level>", methods=["GET"])
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

@move_bp.route("/pokemon/<int:pokemon_id>/base_stats", methods=["GET"])
def get_pokemon_base_stats_route(pokemon_id: int):
    """Get base stats for a Pokémon species"""
    from database_service import PokemonDatabase
    db = PokemonDatabase()
    base_stats = db.get_pokemon_base_stats(pokemon_id)
    if base_stats:
        return jsonify(base_stats), 200
    return jsonify({"error": "Pokémon not found"}), 404

@move_bp.route("/calculate_stats", methods=["POST"])
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

@move_bp.route("/pokemon/<int:pokemon_id>/available_moves", methods=["GET"])
def get_available_moves(pokemon_id: int):
    """Get all moves a Pokémon can learn up to a specific level"""
    level = request.args.get('level', type=int)
    if not level:
        return jsonify({"error": "Level parameter is required"}), 400
    
    move_service = MoveService()
    try:
        moves = move_service.get_pokemon_available_moves(pokemon_id, level)
        return jsonify(moves), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@move_bp.route("/moves/<int:move_id>", methods=["GET"])
def get_move_details(move_id: int):
    """Get detailed information about a move"""
    move_service = MoveService()
    try:
        move = move_service.get_move_details(move_id)
        if move:
            return jsonify(move), 200
        return jsonify({"error": "Move not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
