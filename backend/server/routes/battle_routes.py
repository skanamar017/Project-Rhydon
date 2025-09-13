
# --- Imports ---
import uuid
from flask import Blueprint, request, jsonify
from routes.pokemon_routes import get_team_pokemons

# --- Blueprint ---
battle_routes = Blueprint('battle_routes', __name__)


# In-memory storage for battles and parties (for demo purposes)
battles = {}
parties = {}

@battle_routes.route('/party/create', methods=['POST'])
def create_party():
	data = request.get_json()
	party = data.get('party', [])
	if not party:
		return jsonify({'error': 'Party data required.'}), 400
	party_id = str(uuid.uuid4())
	parties[party_id] = party
	return jsonify({'party_id': party_id, 'message': 'Party created.'})

def gen1_damage(level, power, atk, defense):
	"""
	Basic Gen 1-2 Pokémon damage formula (ignoring modifiers for simplicity):
	https://www.smogon.com/dex/ss/formats/gen1ou/
	"""
	damage = (((2 * level // 5 + 2) * power * atk // defense) // 50) + 2
	return max(1, damage)

def initialize_party(party):
	# Each Pokémon: { 'pokemon_id', 'nickname', 'level', 'max_hp', 'current_hp', ... }
	# For demo, assume 'ev_hp' is max_hp
	return [
		{
			**poke,
			'max_hp': poke.get('ev_hp', 100),
			'current_hp': poke.get('ev_hp', 100),
		}
		for poke in party
	]

@battle_routes.route('/battle/start', methods=['POST'])
def start_battle():
	data = request.get_json()
	# Accept either full teams or party_ids
	teams = data.get('teams', [])
	party_ids = data.get('party_ids', [])
	if teams and len(teams) == 2:
		team_parties = [teams[0].get('party', []), teams[1].get('party', [])]
	elif party_ids and len(party_ids) == 2:
		# Look up parties by ID
		try:
			team_parties = [parties[party_ids[0]], parties[party_ids[1]]]
		except KeyError:
			return jsonify({'error': 'One or both party IDs not found.'}), 404
	else:
		return jsonify({'error': 'Provide either two teams or two party_ids.'}), 400

	battle_id = str(uuid.uuid4())
	battles[battle_id] = {
		'teams': [
			{
				'party': initialize_party(team_parties[0]),
				'active_idx': 0
			},
			{
				'party': initialize_party(team_parties[1]),
				'active_idx': 0
			}
		],
		'state': 'ongoing',
		'log': [],
		'turn': 1,
		'winner': None
	}
	return jsonify({'battle_id': battle_id, 'message': 'Battle started.'})

@battle_routes.route('/battle/move', methods=['POST'])
def make_move():
	data = request.get_json()
	battle_id = data.get('battle_id')
	moves = data.get('moves')  # Expect: [{'move': ..., 'team': 0}, {'move': ..., 'team': 1}]
	if battle_id not in battles:
		return jsonify({'error': 'Battle not found.'}), 404
	battle = battles[battle_id]
	if battle['state'] != 'ongoing':
		return jsonify({'error': 'Battle is over.', 'winner': battle['winner']}), 400


	# Determine move order by speed stat
	t0 = battle['teams'][0]
	t1 = battle['teams'][1]
	p0 = t0['party'][t0['active_idx']]
	p1 = t1['party'][t1['active_idx']]
	m0 = moves[0]
	m1 = moves[1]
	speed0 = p0.get('ev_speed', 50)
	speed1 = p1.get('ev_speed', 50)

	# If speeds are equal, team 0 goes first
	if speed0 >= speed1:
		# Team 0 attacks first
		dmg0 = gen1_damage(p0['level'], m0.get('power', 40), p0.get('ev_attack', 50), p1.get('ev_defense', 50))
		p1['current_hp'] = max(0, p1['current_hp'] - dmg0)
		# If p1 survived, it attacks back
		if p1['current_hp'] > 0:
			dmg1 = gen1_damage(p1['level'], m1.get('power', 40), p1.get('ev_attack', 50), p0.get('ev_defense', 50))
			p0['current_hp'] = max(0, p0['current_hp'] - dmg1)
		else:
			dmg1 = 0
	else:
		# Team 1 attacks first
		dmg1 = gen1_damage(p1['level'], m1.get('power', 40), p1.get('ev_attack', 50), p0.get('ev_defense', 50))
		p0['current_hp'] = max(0, p0['current_hp'] - dmg1)
		# If p0 survived, it attacks back
		if p0['current_hp'] > 0:
			dmg0 = gen1_damage(p0['level'], m0.get('power', 40), p0.get('ev_attack', 50), p1.get('ev_defense', 50))
			p1['current_hp'] = max(0, p1['current_hp'] - dmg0)
		else:
			dmg0 = 0

	log_entry = {
		'turn': battle['turn'],
		'moves': [
			{'team': 0, 'move': m0['move'], 'damage': dmg0, 'target_hp': p1['current_hp']},
			{'team': 1, 'move': m1['move'], 'damage': dmg1, 'target_hp': p0['current_hp']}
		]
	}
	battle['log'].append(log_entry)

	# Check for fainting and send out next Pokémon if needed
	for i, team in enumerate(battle['teams']):
		active = team['party'][team['active_idx']]
		if active['current_hp'] <= 0:
			# Find next available Pokémon
			next_idx = None
			for idx, poke in enumerate(team['party']):
				if poke['current_hp'] > 0:
					next_idx = idx
					break
			if next_idx is not None:
				team['active_idx'] = next_idx
			else:
				# All fainted
				battle['state'] = 'finished'
				battle['winner'] = 1 - i  # Other team wins

	battle['turn'] += 1
	return jsonify({'message': 'Turn complete.', 'log': log_entry, 'state': battle['state'], 'winner': battle['winner']})

@battle_routes.route('/battle/status', methods=['GET'])
def battle_status():
	battle_id = request.args.get('battle_id')
	if battle_id not in battles:
		return jsonify({'error': 'Battle not found.'}), 404
	battle = battles[battle_id]
	return jsonify({
		'battle_id': battle_id,
		'state': battle['state'],
		'log': battle['log'],
		'turn': battle['turn'],
		'teams': battle['teams'],
		'winner': battle['winner']
	})

@battle_routes.route('/party/from_team/<int:team_id>', methods=['POST'])
def create_party_from_team(team_id):
	# Use the get_team_pokemons function from pokemon_routes
	# It returns a Flask Response, so we need to extract the JSON data
	resp = get_team_pokemons(team_id)
	if resp.status_code != 200:
		return resp
	party = resp.get_json()
	if not party:
		return jsonify({'error': 'No Pokémon found for this team.'}), 404
	party_id = str(uuid.uuid4())
	parties[party_id] = party
	return jsonify({'party_id': party_id, 'message': f'Party created from team {team_id}.'})
