from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from database.database import PokemonDatabase

pokedex_bp = Blueprint('pokedex', __name__)

@pokedex_bp.route("/pokedex", methods=["GET"])
@cross_origin()
def get_pokedex():
    """List all Pokémon with optional type, search, and pagination"""
    db = PokemonDatabase()
    poke_type = request.args.get("type")
    search = request.args.get("search")
    pokedex = db.get_pokedex(name_filter=search, type_filter=poke_type)
    return jsonify(pokedex), 200

@pokedex_bp.route("/pokedex/<int:pokemon_id>", methods=["GET"])
@cross_origin()
def get_pokemon_details(pokemon_id):
    db = PokemonDatabase()
    details = db.get_pokemon_details(pokemon_id)
    if details:
        return jsonify(details), 200
    return jsonify({"error": "Pokémon not found"}), 404

@pokedex_bp.route("/pokedex/types", methods=["GET"])
@cross_origin()
def get_pokemon_types():
    db = PokemonDatabase()
    types = db.get_all_pokemon_types()
    return jsonify(types), 200

@pokedex_bp.route("/pokedex/<int:pokemon_id>/base_stats", methods=["GET"])
@cross_origin()
def get_pokemon_base_stats_route(pokemon_id: int):
    db = PokemonDatabase()
    base_stats = db.get_pokemon_base_stats(pokemon_id)
    if base_stats:
        return jsonify(base_stats), 200
    return jsonify({"error": "Pokémon not found"}), 404
