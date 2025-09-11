"""
Flask route handlers for move management endpoints.
"""

from flask import Blueprint, request, jsonify
import sqlite3
from database.database import Gen1StatCalculator, PokemonDatabase
from flask_cors import cross_origin

move_bp = Blueprint('moves', __name__)

@move_bp.route("/Pokemon/", methods=["GET"])
@cross_origin()
def get_all_pokemon():
    """Get all Pokemon with optional type filtering"""
    poke_type = request.args.get("type")
    db = PokemonDatabase()
    db_path = db.db_path
    with sqlite3.connect(db_path) as conn:
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
    """Get all moves for a Pokemon including those learned from previous evolutions."""
    max_level = request.args.get("max_level", type=int)
    move_type = request.args.get("type")  # level-up, tm-hm, or all
    
    with sqlite3.connect("pokemon.db") as conn:
        conn.row_factory = sqlite3.Row
        
        # Get evolution chain for this Pokemon
        def get_evolution_chain(current_id: int) -> list:
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
    
    db = PokemonDatabase()
    try:
        moves = db.get_pokemon_available_moves(pokemon_id, level)
        return jsonify(moves), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@move_bp.route("/moves/<int:move_id>", methods=["GET"])
def get_move_details(move_id: int):
    """Get detailed information about a move"""
    db = PokemonDatabase()
    try:
        move = db.get_move_details(move_id)
        if move:
            return jsonify(move), 200
        return jsonify({"error": "Move not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
