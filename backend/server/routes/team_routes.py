"""
Flask route handlers for team management endpoints.
Separated from main Flask app for better organization.
"""

from flask import Blueprint, request, jsonify
from database.database import Team, TeamPokemon, PokemonDatabase

team_bp = Blueprint('teams', __name__)

@team_bp.route("/", methods=["POST"])
def create_team():
    db = PokemonDatabase()
    data = request.get_json()
    team = Team(**data)
    try:
        created = db.create_team(team)
        return jsonify(created.model_dump()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@team_bp.route("/<int:team_id>", methods=["GET"])
def get_team(team_id):
    db = PokemonDatabase()
    team = db.get_team(team_id)
    if team:
        return jsonify(team.model_dump()), 200
    return jsonify({"error": "Team not found"}), 404

@team_bp.route("/", methods=["GET"])
def get_all_teams():
    db = PokemonDatabase()
    teams = db.get_all_teams()
    return jsonify([t.model_dump() for t in teams]), 200

@team_bp.route("/<int:team_id>", methods=["PUT"])
def update_team(team_id):
    db = PokemonDatabase()
    data = request.get_json()
    team = Team(**data)
    updated = db.update_team(team_id, team)
    if updated:
        return jsonify(updated.model_dump()), 200
    return jsonify({"error": "Team not found"}), 404

@team_bp.route("/<int:team_id>", methods=["DELETE"])
def delete_team(team_id):
    db = PokemonDatabase()
    if db.delete_team(team_id):
        return jsonify({"message": "Team deleted successfully"}), 200
    return jsonify({"error": "Team not found"}), 404
