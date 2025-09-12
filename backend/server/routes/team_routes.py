"""
Flask route handlers for team management endpoints.
Separated from main Flask app for better organization.
"""

from flask import Blueprint, request, jsonify
from database.database import Team, TeamPokemon, PokemonDatabase

def get_user_id():
    user_id = request.headers.get('X-User-Id')
    if not user_id:
        return None
    try:
        return int(user_id)
    except ValueError:
        return None

team_bp = Blueprint('teams', __name__)

@team_bp.route("/", methods=["POST"])
def create_team():
    db = PokemonDatabase()
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Missing or invalid X-User-Id header."}), 401
    data = request.get_json()
    team = Team(**data)
    try:
        created = db.create_team(team, user_id)
        return jsonify(created.model_dump()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@team_bp.route("/<int:team_id>", methods=["GET"])
def get_team(team_id):
    db = PokemonDatabase()
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Missing or invalid X-User-Id header."}), 401
    team = db.get_team(team_id)
    if team and hasattr(team, 'user_id') and getattr(team, 'user_id', None) == user_id:
        return jsonify(team.model_dump()), 200
    return jsonify({"error": "Team not found or access denied."}), 404

@team_bp.route("/", methods=["GET"])
def get_all_teams():
    db = PokemonDatabase()
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Missing or invalid X-User-Id header."}), 401
    teams = db.get_teams_by_user(user_id)
    return jsonify([t.model_dump() for t in teams]), 200

@team_bp.route("/<int:team_id>", methods=["PUT"])
def update_team(team_id):
    db = PokemonDatabase()
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Missing or invalid X-User-Id header."}), 401
    team = db.get_team(team_id)
    if not team or getattr(team, 'user_id', None) != user_id:
        return jsonify({"error": "Team not found or access denied."}), 404
    data = request.get_json()
    updated = db.update_team(team_id, Team(**data))
    if updated:
        return jsonify(updated.model_dump()), 200
    return jsonify({"error": "Team not found"}), 404

@team_bp.route("/<int:team_id>", methods=["DELETE"])
def delete_team(team_id):
    db = PokemonDatabase()
    user_id = get_user_id()
    if not user_id:
        return jsonify({"error": "Missing or invalid X-User-Id header."}), 401
    team = db.get_team(team_id)
    if not team or getattr(team, 'user_id', None) != user_id:
        return jsonify({"error": "Team not found or access denied."}), 404
    if db.delete_team(team_id):
        return jsonify({"message": "Team deleted successfully"}), 200
    return jsonify({"error": "Team not found"}), 404
