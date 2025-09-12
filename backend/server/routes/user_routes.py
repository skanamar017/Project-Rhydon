"""
Flask route handlers for user registration and login endpoints.
"""

from flask import Blueprint, request, jsonify
from database.services.database_service import PokemonDatabase

user_bp = Blueprint('users', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    db = PokemonDatabase()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400
    try:
        user = db.register_user(username, password)
        return jsonify({'id': user.id, 'username': user.username}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@user_bp.route('/login', methods=['POST'])
def login():
    db = PokemonDatabase()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400
    user = db.authenticate_user(username, password)
    if user:
        return jsonify({'id': user.id, 'username': user.username}), 200
    else:
        return jsonify({'error': 'Invalid username or password.'}), 401
