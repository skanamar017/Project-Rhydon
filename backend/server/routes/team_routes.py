"""
Flask route handlers for team management endpoints.
Separated from main Flask app for better organization.
"""

from flask import Blueprint, request, jsonify, session
from database.database import Team, TeamPokemon, PokemonDatabase
from routes.auth_utils import login_required

team_bp = Blueprint('teams', __name__)

@team_bp.route("/", methods=["POST"])
@login_required
def create_team():
    db = PokemonDatabase()
    data = request.get_json()
    user_id = session['user_id']
    team = Team(**data, user_id=user_id)
    try:
        created = db.create_team(team)
        return jsonify(created.model_dump()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@team_bp.route("/<int:team_id>", methods=["GET"])
@login_required
def get_team(team_id):
    db = PokemonDatabase()
    user_id = session['user_id']
    team = db.get_team(team_id)
    if team and getattr(team, 'user_id', None) == user_id:
        return jsonify(team.model_dump()), 200
    return jsonify({"error": "Team not found or access denied"}), 404

@team_bp.route("/", methods=["GET"])
@login_required
def get_all_teams():
    db = PokemonDatabase()
    user_id = session['user_id']
    teams = db.get_all_teams(user_id=user_id)
    return jsonify([t.model_dump() for t in teams]), 200

@team_bp.route("/<int:team_id>", methods=["PUT"])
@login_required
def update_team(team_id):
    db = PokemonDatabase()
    user_id = session['user_id']
    data = request.get_json()
    team = db.get_team(team_id)
    if not team or getattr(team, 'user_id', None) != user_id:
        return jsonify({"error": "Team not found or access denied"}), 404
    updated_team = Team(**data, user_id=user_id)
    updated = db.update_team(team_id, updated_team)
    if updated:
        return jsonify(updated.model_dump()), 200
    return jsonify({"error": "Team not found"}), 404

@team_bp.route("/<int:team_id>", methods=["DELETE"])
@login_required
def delete_team(team_id):
    db = PokemonDatabase()
    user_id = session['user_id']
    team = db.get_team(team_id)
    if not team or getattr(team, 'user_id', None) != user_id:
        return jsonify({"error": "Team not found or access denied"}), 404
    if db.delete_team(team_id):
        return jsonify({"message": "Team deleted successfully"}), 200
    return jsonify({"error": "Team not found"}), 404
