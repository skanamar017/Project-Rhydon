# Combined Trainer and Pokémon info endpoint

from flask import Flask, request, jsonify, make_response
from database import PokemonDatabase, Trainer, TrainerPokemon
from typing import List
import json
import sqlite3
from flask_cors import CORS

app = Flask(__name__)

# Simple CORS configuration - REMOVE the complex one
CORS(app)

db = PokemonDatabase()

@app.route("/", methods=["GET"])
def home():
    return {"message": "Pokemon Trainer API"}

# Trainer Endpoints
@app.route("/Trainers/", methods=["POST"])
def create_trainer():
    data = request.get_json()
    trainer = Trainer(**data)
    try:
        created = db.create_trainer(trainer)
        return jsonify(created.model_dump()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/Trainers/<int:trainer_id>", methods=["GET"])
def get_trainer(trainer_id):
    trainer = db.get_trainer(trainer_id)
    if trainer:
        return jsonify(trainer.model_dump()), 200
    return jsonify({"error": "Trainer not found"}), 404

@app.route("/Trainers/", methods=["GET"])
def get_all_trainers():
    trainers = db.get_all_trainers()
    return jsonify([t.model_dump() for t in trainers]), 200

@app.route("/Trainers/<int:trainer_id>", methods=["PUT"])
def update_trainer(trainer_id):
    data = request.get_json()
    trainer = Trainer(**data)
    updated = db.update_trainer(trainer_id, trainer)
    if updated:
        return jsonify(updated.model_dump()), 200
    return jsonify({"error": "Trainer not found"}), 404

@app.route("/Trainers/<int:trainer_id>", methods=["DELETE"])
def delete_trainer(trainer_id):
    if db.delete_trainer(trainer_id):
        return jsonify({"message": "Trainer deleted successfully"}), 200
    return jsonify({"error": "Trainer not found"}), 404

# TrainerPokemon Endpoints
@app.route("/Trainers/<int:trainer_id>/TrainerPokemon/", methods=["POST"])
def create_trainer_pokemon(trainer_id):
    try:
        data = request.get_json()
        print(f"[DEBUG] Creating Pokemon for trainer {trainer_id} with data: {data}")
        
        # Ensure trainer_id is set in the data
        data['trainer_id'] = trainer_id
        
        # Create TrainerPokemon object
        tp = TrainerPokemon(**data)
        created = db.create_trainer_pokemon(tp)
        
        print(f"[DEBUG] Successfully created Pokemon: {created}")
        return jsonify(created.model_dump()), 201
    except Exception as e:
        print(f"[ERROR] Failed to create Pokemon: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/Trainers/<int:trainer_id>/TrainerPokemon/<int:tp_id>", methods=["GET"])
def get_trainer_pokemon(trainer_id, tp_id):
    tp = db.get_trainer_pokemon(tp_id)
    if tp:
        return jsonify(tp.model_dump()), 200
    return jsonify({"error": "TrainerPokemon not found"}), 404

@app.route("/Trainers/<int:trainer_id>/TrainerPokemon/<int:tp_id>/stats", methods=["GET"])
def get_trainer_pokemon_stats_route(trainer_id, tp_id):
    """Get calculated stats for a trainer's Pokémon"""
    details = db.get_trainer_pokemon_with_stats(tp_id)
    if details:
        return jsonify(details), 200
    return jsonify({"error": "Trainer Pokémon not found"}), 404

@app.route("/Trainers/<int:trainer_id>/TrainerPokemon/", methods=["GET"])
@app.route("/Trainers/<int:trainer_id>/TrainerPokemon", methods=["GET"])
def get_trainer_pokemons(trainer_id):
    print(f"[DEBUG] get_trainer_pokemons called for trainer_id={trainer_id}")
    tps = db.get_trainer_pokemons_by_trainer_id(trainer_id)
    # Since tps is now a List[dict], we don't need .model_dump()
    return jsonify(tps), 200

@app.route("/Trainers/<int:trainer_id>/TrainerPokemon/<int:tp_id>", methods=["PUT"])
def update_trainer_pokemon(trainer_id, tp_id):
    try:
        data = request.get_json()
        print(f"[DEBUG] Updating Pokemon {tp_id} with data: {data}")
        
        # Get the existing trainer pokemon first
        existing_tp = db.get_trainer_pokemon(tp_id)
        if not existing_tp:
            return jsonify({"error": "TrainerPokemon not found"}), 404
        
        # Update only the fields that are provided
        update_data = existing_tp.model_dump()
        if 'nickname' in data:
            update_data['nickname'] = data['nickname']
        if 'level' in data:
            update_data['level'] = data['level']
        
        # Create updated TrainerPokemon object with all required fields
        tp = TrainerPokemon(**update_data)
        updated = db.update_trainer_pokemon(tp_id, tp)
        
        if updated:
            print(f"[DEBUG] Successfully updated Pokemon: {updated}")
            return jsonify(updated.model_dump()), 200
        else:
            return jsonify({"error": "Failed to update TrainerPokemon"}), 500
            
    except Exception as e:
        print(f"[ERROR] Failed to update Pokemon: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/Trainers/<int:trainer_id>/TrainerPokemon/<int:tp_id>", methods=["DELETE"])
def delete_trainer_pokemon(trainer_id, tp_id):
    if db.delete_trainer_pokemon(tp_id):
        return jsonify({"message": "TrainerPokemon deleted successfully"}), 200
    return jsonify({"error": "TrainerPokemon not found"}), 404

@app.route("/Pokemon/", methods=["GET"])
def get_all_pokemon():
    # Optional: filter by query param, e.g., ?type=Fire
    poke_type = request.args.get("type")
    with sqlite3.connect("pokemon.db") as conn:
        conn.row_factory = sqlite3.Row
        if poke_type:
            cursor = conn.execute("SELECT * FROM Pokemon WHERE type1 = ? OR type2 = ?", (poke_type, poke_type))
        else:
            cursor = conn.execute("SELECT * FROM Pokemon")
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
