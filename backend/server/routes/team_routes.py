"""
Flask route handlers for team management endpoints.
Separated from main Flask app for better organization.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from database.database import Team, TeamPokemon, PokemonDatabase

team_bp = Blueprint('teams', __name__)

@team_bp.route("/", methods=["POST"])
@login_required
def create_team():
    db = PokemonDatabase()
    data = request.get_json()
    team = Team(**data, account_id=current_user.id)
    try:
        created = db.create_team(team)
        return jsonify(created.model_dump()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@team_bp.route("/<int:team_id>", methods=["GET"])
@login_required
def get_team(team_id):
    db = PokemonDatabase()
    team = db.get_team(team_id)
    if team and team.account_id == current_user.id:
        return jsonify(team.model_dump()), 200
    return jsonify({"error": "Team not found or not owned by user"}), 404

@team_bp.route("/", methods=["GET"])
@login_required
def get_all_teams():
    db = PokemonDatabase()
    teams = db.get_all_teams(account_id=current_user.id)
    return jsonify([t.model_dump() for t in teams]), 200

@team_bp.route("/<int:team_id>", methods=["PUT"])
@login_required
def update_team(team_id):
    db = PokemonDatabase()
    data = request.get_json()
    team = Team(**data, account_id=current_user.id)
    db_team = db.get_team(team_id)
    if not db_team or db_team.account_id != current_user.id:
        return jsonify({"error": "Team not found or not owned by user"}), 404
    updated = db.update_team(team_id, team)
    if updated:
        return jsonify(updated.model_dump()), 200
    return jsonify({"error": "Update failed"}), 400

@team_bp.route("/<int:team_id>", methods=["DELETE"])
@login_required
def delete_team(team_id):
    db = PokemonDatabase()
    db_team = db.get_team(team_id)
    if not db_team or db_team.account_id != current_user.id:
        return jsonify({"error": "Team not found or not owned by user"}), 404
    if db.delete_team(team_id):
        return jsonify({"message": "Team deleted successfully"}), 200
    return jsonify({"error": "Delete failed"}), 400
