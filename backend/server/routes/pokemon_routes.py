# --- PartyPokemon Moves Endpoint (for CORS and move management) ---
from flask_cors import cross_origin

"""
Flask route handlers for team pokemon management endpoints.
"""

from flask import Blueprint, request, jsonify
from backend.models import PartyPokemon
from backend.database_service import PokemonDatabase

pokemon_bp = Blueprint('pokemon', __name__)


@pokemon_bp.route("/", methods=["POST"])
def create_party_pokemon():
    db = PokemonDatabase()
    try:
        data = request.get_json()
        # Validate Effort Values (EVs)
        ev_fields = ['ev_hp', 'ev_attack', 'ev_defense', 'ev_speed', 'ev_special']
        for ev_field in ev_fields:
            if ev_field in data:
                ev_value = data[ev_field]
                if not isinstance(ev_value, int) or ev_value < 0 or ev_value > 65535:
                    return jsonify({"error": f"{ev_field} must be between 0 and 65535"}), 400
        tp = PartyPokemon(**data)
        created = db.create_party_pokemon(tp)
        return jsonify(created.model_dump()), 201
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pokemon_bp.route("/<int:tp_id>", methods=["GET"])
def get_party_pokemon(tp_id):
    db = PokemonDatabase()
    tp = db.get_party_pokemon(tp_id)
    if tp:
        return jsonify(tp.model_dump()), 200
    return jsonify({"error": "PartyPokemon not found"}), 404


@pokemon_bp.route("/", methods=["GET"])
def get_party_pokemons():
    db = PokemonDatabase()
    tps = db.get_party_pokemons()
    return jsonify(tps), 200


@pokemon_bp.route("/count", methods=["GET"])
def get_party_pokemon_count():
    """Get the current number of Pokemon in the party"""
    db = PokemonDatabase()
    try:
        count = db.get_party_pokemon_count()
        return jsonify({
            "pokemon_count": count,
            "can_add_more": count < 6,
            "can_remove": count > 1
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pokemon_bp.route("/<int:tp_id>", methods=["PUT"])
def update_party_pokemon(tp_id):
    db = PokemonDatabase()
    try:
        data = request.get_json()
        # Get existing pokemon
        existing_tp = db.get_party_pokemon(tp_id)
        if not existing_tp:
            return jsonify({"error": "PartyPokemon not found"}), 404
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
        tp = PartyPokemon(**update_data)
        updated = db.update_party_pokemon(tp_id, tp)
        if updated:
            return jsonify(updated.model_dump()), 200
        else:
            return jsonify({"error": "Failed to update PartyPokemon"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pokemon_bp.route("/<int:tp_id>", methods=["DELETE"])
def delete_party_pokemon(tp_id):
    db = PokemonDatabase()
    try:
        if db.delete_party_pokemon(tp_id):
            return jsonify({"message": "PartyPokemon deleted successfully"}), 200
        return jsonify({"error": "PartyPokemon not found"}), 404
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@pokemon_bp.route("/<int:tp_id>/stats", methods=["GET"])
def get_party_pokemon_stats(tp_id):
    db = PokemonDatabase()
    tp = db.get_party_pokemon(tp_id)
    if not tp:
        return jsonify({"error": "PartyPokemon not found"}), 404
    # Get base stats for this species
    base_stats = db.get_pokemon_base_stats(tp.pokemon_id)
    if not base_stats:
        return jsonify({"error": "Base stats not found"}), 404
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
    from database.database import Gen1StatCalculator
    stats = Gen1StatCalculator.calculate_all_stats(base_stats, tp.level, ivs, evs)
    return jsonify(stats.model_dump()), 200