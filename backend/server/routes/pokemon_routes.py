# --- TeamPokemon Moves Endpoint (for CORS and move management) ---
from flask_cors import cross_origin
from flask_login import login_required, current_user

"""
Flask route handlers for team pokemon management endpoints.
"""

from flask import Blueprint, request, jsonify
from database.database import TeamPokemon, PokemonDatabase

pokemon_bp = Blueprint('pokemon', __name__)

def _team_belongs_to_current_user(team_id):
    db = PokemonDatabase()
    team = db.get_team(team_id)
    return team and team.account_id == current_user.id

@pokemon_bp.route("/<int:team_id>/TeamPokemon/", methods=["POST"])
@login_required
def create_team_pokemon(team_id):
    if not _team_belongs_to_current_user(team_id):
        return jsonify({"error": "Forbidden: Not your team"}), 403
    db = PokemonDatabase()
    try:
        data = request.get_json()
        data['team_id'] = team_id
        
        # Validate Effort Values (EVs)
        ev_fields = ['ev_hp', 'ev_attack', 'ev_defense', 'ev_speed', 'ev_special']
        for ev_field in ev_fields:
            if ev_field in data:
                ev_value = data[ev_field]
                if not isinstance(ev_value, int) or ev_value < 0 or ev_value > 65535:
                    return jsonify({"error": f"{ev_field} must be between 0 and 65535"}), 400
        
        tp = TeamPokemon(**data)
        created = db.create_team_pokemon(tp)
        return jsonify(created.model_dump()), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pokemon_bp.route("/<int:team_id>/TeamPokemon/<int:tp_id>", methods=["GET"])
@login_required
def get_team_pokemon(team_id, tp_id):
    db = PokemonDatabase()
    tp = db.get_team_pokemon(tp_id)
    if tp and _team_belongs_to_current_user(team_id):
        return jsonify(tp.model_dump()), 200
    return jsonify({"error": "TeamPokemon not found or not owned by user"}), 404

@pokemon_bp.route("/<int:team_id>/TeamPokemon/", methods=["GET"])
@pokemon_bp.route("/<int:team_id>/TeamPokemon", methods=["GET"])
@login_required
def get_team_pokemons(team_id):
    if not _team_belongs_to_current_user(team_id):
        return jsonify({"error": "Forbidden: Not your team"}), 403
    db = PokemonDatabase()
    tps = db.get_team_pokemons_by_team_id(team_id)
    return jsonify(tps), 200

@pokemon_bp.route("/<int:team_id>/TeamPokemon/count", methods=["GET"])
@login_required
def get_team_pokemon_count(team_id):
    if not _team_belongs_to_current_user(team_id):
        return jsonify({"error": "Forbidden: Not your team"}), 403
    db = PokemonDatabase()
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

@pokemon_bp.route("/<int:team_id>/TeamPokemon/<int:tp_id>", methods=["PUT"])
@login_required
def update_team_pokemon(team_id, tp_id):
    if not _team_belongs_to_current_user(team_id):
        return jsonify({"error": "Forbidden: Not your team"}), 403
    db = PokemonDatabase()
    try:
        data = request.get_json()
        
        # Get existing pokemon
        existing_tp = db.get_team_pokemon(tp_id)
        if not existing_tp:
            return jsonify({"error": "TeamPokemon not found"}), 404
        
        # Update fields
        update_data = existing_tp.model_dump()
        
        # Basic fields
        for field in ['nickname', 'level', 'status', 'current_hp']:
            if field in data:
                update_data[field] = data[field]
        
        # Validate and update EVs
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
        
        tp = TeamPokemon(**update_data)
        updated = db.update_team_pokemon(tp_id, tp)
        
        if updated:
            return jsonify(updated.model_dump()), 200
        else:
            return jsonify({"error": "Failed to update TeamPokemon"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pokemon_bp.route("/<int:team_id>/TeamPokemon/<int:tp_id>", methods=["DELETE"])
@login_required
def delete_team_pokemon(team_id, tp_id):
    if not _team_belongs_to_current_user(team_id):
        return jsonify({"error": "Forbidden: Not your team"}), 403
    db = PokemonDatabase()
    try:
        if db.delete_team_pokemon(tp_id):
            return jsonify({"message": "TeamPokemon deleted successfully"}), 200
        return jsonify({"error": "TeamPokemon not found"}), 404
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pokemon_bp.route("/<int:team_id>/TeamPokemon/<int:tp_id>/stats", methods=["GET"])
def get_team_pokemon_stats_route(team_id, tp_id):
    """Get calculated stats for a team's Pokémon"""
    db = PokemonDatabase()
    details = db.get_team_pokemon_with_stats(tp_id)
    if details:
        return jsonify(details), 200
    return jsonify({"error": "Team Pokémon not found"}), 404

@pokemon_bp.route("/<int:team_id>/TeamPokemon/<int:tp_id>/moves", methods=["GET", "PUT", "OPTIONS"])
@cross_origin()
def team_pokemon_moves(team_id, tp_id):
    db = PokemonDatabase()
    tp = db.get_team_pokemon(tp_id)
    if not tp:
        return jsonify({"error": "TeamPokemon not found"}), 404

    if request.method == "OPTIONS":
        # CORS preflight
        return ('', 204)

    if request.method == "GET":
        # Return current moves for this TeamPokemon
        moves = []
        for move_id in [tp.move1_id, tp.move2_id, tp.move3_id, tp.move4_id]:
            if move_id:
                move = db.get_move_by_id(move_id)
                if move:
                    moves.append(move.model_dump())
        return jsonify({"current_moves": moves}), 200

    if request.method == "PUT":
        data = request.get_json()
        move_ids = data.get('move_ids', [])
        # Pad or trim to 4
        move_ids = (move_ids + [None]*4)[:4]
        tp.move1_id, tp.move2_id, tp.move3_id, tp.move4_id = move_ids
        updated = db.update_team_pokemon(tp_id, tp)
        if updated:
            return jsonify({"message": "Moves updated", "current_moves": move_ids}), 200
        else:
            return jsonify({"error": "Failed to update moves"}), 500
