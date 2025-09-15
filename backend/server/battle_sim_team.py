import requests
import sys

API = "http://localhost:5001"


def get_team_pokemon(team_id):
    resp = requests.get(f"{API}/Teams/{team_id}/TeamPokemon/")
    resp.raise_for_status()
    return resp.json()

def get_move_details(move_id):
    resp = requests.get(f"{API}/moves/{move_id}")
    if resp.status_code == 200:
        return resp.json()
    return None

def simulate_battle(tp1, tp2, move_slot1=1, move_slot2=1):
    # Pick move_id from TeamPokemon object
    move1_id = tp1.get(f"move{move_slot1}_id")
    move2_id = tp2.get(f"move{move_slot2}_id")
    move1 = get_move_details(move1_id) if move1_id else None
    move2 = get_move_details(move2_id) if move2_id else None
    if not move1 or not move2:
        print("Invalid move(s) for one of the Pokémon.")
        return
    payload = {
        "pokemon1": {
            "id": tp1["pokemon_id"],
            "level": tp1["level"],
            "move_id": move1_id,
            "nickname": tp1.get("nickname"),
            "stats": {
                "hp": tp1.get("calculated_hp", tp1.get("current_hp")),
                "attack": tp1.get("calculated_attack"),
                "defense": tp1.get("calculated_defense"),
                "speed": tp1.get("calculated_speed"),
                "special": tp1.get("calculated_special")
            }
        },
        "pokemon2": {
            "id": tp2["pokemon_id"],
            "level": tp2["level"],
            "move_id": move2_id,
            "nickname": tp2.get("nickname"),
            "stats": {
                "hp": tp2.get("calculated_hp", tp2.get("current_hp")),
                "attack": tp2.get("calculated_attack"),
                "defense": tp2.get("calculated_defense"),
                "speed": tp2.get("calculated_speed"),
                "special": tp2.get("calculated_special")
            }
        }
    }
    resp = requests.post(f"{API}/battle/simulate", json=payload)
    print(resp.json())

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python battle_sim_team.py <team1_id> <tp1_index> <team2_id> <tp2_index> [move_slot1] [move_slot2]")
        sys.exit(1)
    team1_id = int(sys.argv[1])
    tp1_index = int(sys.argv[2])
    team2_id = int(sys.argv[3])
    tp2_index = int(sys.argv[4])
    move_slot1 = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    move_slot2 = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    team1_pokemon = get_team_pokemon(team1_id)
    team2_pokemon = get_team_pokemon(team2_id)
    if tp1_index >= len(team1_pokemon) or tp2_index >= len(team2_pokemon):
        print("Invalid TeamPokemon indices.")
        sys.exit(1)
    tp1 = team1_pokemon[tp1_index]
    tp2 = team2_pokemon[tp2_index]
    simulate_battle(tp1, tp2, move_slot1, move_slot2)
