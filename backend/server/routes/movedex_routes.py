from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from database.database import PokemonDatabase

movedex_bp = Blueprint('movedex', __name__)

@movedex_bp.route("/movedex", methods=["GET"])
@cross_origin()
def get_movedex():
    """List all moves with optional type, search, and pagination"""
    db = PokemonDatabase()
    move_type = request.args.get("type")
    search = request.args.get("search")
    limit = request.args.get("limit")
    if limit is not None:
        limit = int(limit)
    movedex = db.get_movedex(move_type=move_type, search=search, limit=limit) if limit else db.get_movedex(move_type=move_type, search=search, limit=10000)
    return jsonify(movedex), 200

@movedex_bp.route("/movedex/<int:move_id>", methods=["GET"])
@cross_origin()
def get_move_details(move_id):
    db = PokemonDatabase()
    details = db.get_move_details(move_id)
    if details:
        return jsonify(details), 200
    return jsonify({"error": "Move not found"}), 404

@movedex_bp.route("/movedex/types", methods=["GET"])
@cross_origin()
def get_move_types():
    db = PokemonDatabase()
    types = db.get_all_move_types()
    return jsonify(types), 200
