from flask import request, jsonify, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from server.user_model import User
from database.services.database_service import PokemonDatabase

user_bp = Blueprint('user', __name__)

from flask_cors import cross_origin

@user_bp.route('/register', methods=['POST'])
@cross_origin(supports_credentials=True, origins=["http://127.0.0.1:5001", "null"])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    db = PokemonDatabase()
    if db.get_account_by_username(username):
        return jsonify({'error': 'Username already exists'}), 400
    account = db.create_account(username, password)
    user = User(id=account.id, username=account.username, password_hash=account.password_hash)
    login_user(user)  # Log in the user after registration
    return jsonify({'message': 'Registered and logged in', 'username': user.username})

@user_bp.route('/login', methods=['POST'])
@cross_origin(supports_credentials=True, origins=["http://127.0.0.1:5001", "null"])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    db = PokemonDatabase()
    account = db.verify_account(username, password)
    if not account:
        return jsonify({'error': 'Invalid credentials'}), 401
    user = User(id=account.id, username=account.username, password_hash=account.password_hash)
    login_user(user)
    return jsonify({'message': 'Logged in', 'username': user.username})

@user_bp.route('/logout', methods=['POST'])
@cross_origin(supports_credentials=True, origins=["http://127.0.0.1:5001", "null"])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out'})

@user_bp.route('/me', methods=['GET'])
@cross_origin(supports_credentials=True, origins=["http://127.0.0.1:5001", "null"])
@login_required
def me():
    return jsonify({'id': current_user.id, 'username': current_user.username})