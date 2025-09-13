
from flask import Blueprint, request, jsonify
import uuid

battle_routes = Blueprint('battle_routes', __name__)

# In-memory storage for battles (for demo purposes)
battles = {}

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
	teams = data.get('teams', [])
	if len(teams) != 2:
		return jsonify({'error': 'Exactly two teams required.'}), 400
	battle_id = str(uuid.uuid4())
	# Each team: { 'party': [pokemon, ...] }
	battles[battle_id] = {
		'teams': [
			{
				'party': initialize_party(teams[0].get('party', [])),
				'active_idx': 0
			},
			{
				'party': initialize_party(teams[1].get('party', [])),
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

	# For demo: both teams attack each other in order
	t0 = battle['teams'][0]
	t1 = battle['teams'][1]
	p0 = t0['party'][t0['active_idx']]
	p1 = t1['party'][t1['active_idx']]

	# Dummy move data: {'move': 'Tackle', 'power': 40}
	m0 = moves[0]
	m1 = moves[1]
	# For demo, use level, attack, defense from party dict
	dmg0 = gen1_damage(p0['level'], m0.get('power', 40), p0.get('ev_attack', 50), p1.get('ev_defense', 50))
	dmg1 = gen1_damage(p1['level'], m1.get('power', 40), p1.get('ev_attack', 50), p0.get('ev_defense', 50))

	# Apply damage
	p1['current_hp'] = max(0, p1['current_hp'] - dmg0)
	p0['current_hp'] = max(0, p0['current_hp'] - dmg1)

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
