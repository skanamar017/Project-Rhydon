"""
Move management service for Pokemon team management.
Handles all move-related database operations.
"""

import sqlite3
from typing import List, Optional, Dict

class MoveService:
    def __init__(self, db_path: str = "pokemon.db"):
        self.db_path = db_path

    def get_pokemon_available_moves(self, pokemon_id: int, max_level: int) -> List[dict]:
        """Get all moves a Pokemon can learn up to a specific level"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT DISTINCT pm.move_id, m.name, m.type, m.power, m.accuracy, 
                       m.pp, pm.level_learned, m.effect
                FROM PokemonMoves pm
                JOIN Moves m ON pm.move_id = m.id
                WHERE pm.pokemon_id = ? AND pm.level_learned <= ?
                ORDER BY pm.level_learned, m.name
            """, (pokemon_id, max_level))
            
            moves = []
            for row in cursor.fetchall():
                moves.append({
                    'move_id': row['move_id'],
                    'name': row['name'],
                    'type': row['type'],
                    'power': row['power'],
                    'accuracy': row['accuracy'],
                    'pp': row['pp'],
                    'level_learned': row['level_learned'],
                    'effect_description': row['effect']
                })
            return moves

    def get_pokemon_moves_by_level(self, pokemon_id: int) -> Dict[int, List[dict]]:
        """Get all moves a Pokemon learns grouped by level"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT DISTINCT pm.move_id, m.name, m.type, m.power, m.accuracy, 
                       m.pp, pm.level_learned, m.effect
                FROM PokemonMoves pm
                JOIN Moves m ON pm.move_id = m.id
                WHERE pm.pokemon_id = ?
                ORDER BY pm.level_learned, m.name
            """, (pokemon_id,))
            
            moves_by_level = {}
            for row in cursor.fetchall():
                level = row['level_learned']
                if level not in moves_by_level:
                    moves_by_level[level] = []
                
                moves_by_level[level].append({
                    'move_id': row['move_id'],
                    'name': row['name'],
                    'type': row['type'],
                    'power': row['power'],
                    'accuracy': row['accuracy'],
                    'pp': row['pp'],
                    'effect_description': row['effect']
                })
            return moves_by_level

    def get_pokemon_moves_with_evolutions(self, pokemon_id: int) -> Dict:
        """Get all moves for a Pokemon including those from previous evolutions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get evolution chain
            evolution_chain = self._get_evolution_chain(conn, pokemon_id)
            
            # Get moves from entire evolution chain
            query = """
            SELECT DISTINCT
                pm.move_id,
                m.name as move_name,
                pm.level_learned,
                m.type as move_type,
                m.power,
                m.accuracy,
                m.pp,
                p.name as learned_from_pokemon,
                p.pokedex_number as learned_from_id,
                CASE 
                    WHEN pm.level_learned = 0 THEN 'TM/HM'
                    ELSE 'Level-up'
                END as learn_method
            FROM PokemonMoves pm
            JOIN Moves m ON pm.move_id = m.id
            JOIN Pokemon p ON pm.pokemon_id = p.pokedex_number
            WHERE pm.pokemon_id IN ({})
            ORDER BY pm.level_learned, m.name
            """.format(','.join(['?'] * len(evolution_chain)))
            
            cursor = conn.execute(query, evolution_chain)
            moves = cursor.fetchall()
            
            # Get Pokemon and evolution chain names
            pokemon_cursor = conn.execute("SELECT name FROM Pokemon WHERE pokedex_number = ?", [pokemon_id])
            pokemon_result = pokemon_cursor.fetchone()
            pokemon_name = pokemon_result[0] if pokemon_result else f"Pokemon #{pokemon_id}"
            
            chain_names = {}
            for evo_id in evolution_chain:
                cursor = conn.execute("SELECT name FROM Pokemon WHERE pokedex_number = ?", [evo_id])
                result = cursor.fetchone()
                if result:
                    chain_names[evo_id] = result[0]
            
            return {
                "pokemon_id": pokemon_id,
                "pokemon_name": pokemon_name,
                "evolution_chain": [{"id": evo_id, "name": chain_names.get(evo_id, f"Pokemon #{evo_id}")} 
                                  for evo_id in evolution_chain],
                "total_moves": len(moves),
                "moves": [dict(move) for move in moves]
            }

    def _get_evolution_chain(self, conn, pokemon_id: int) -> List[int]:
        """Get the full evolution chain leading to a Pokemon (including itself)"""
        chain = []
        visited = set()
        
        def find_pre_evolutions(current_id: int):
            if current_id in visited:
                return
            visited.add(current_id)
            
            cursor = conn.execute("""
                SELECT from_pokemon_id FROM Evolution 
                WHERE to_pokemon_id = ?
            """, (current_id,))
            
            pre_evolutions = cursor.fetchall()
            for (pre_evo_id,) in pre_evolutions:
                find_pre_evolutions(pre_evo_id)
                if pre_evo_id not in chain:
                    chain.append(pre_evo_id)
            
            if current_id not in chain:
                chain.append(current_id)
        
        find_pre_evolutions(pokemon_id)
        return chain

    def validate_pokemon_moves(self, pokemon_id: int, level: int, move_ids: List[int]) -> Dict:
        """Validate that a Pokemon can learn the specified moves at their current level"""
        if len(move_ids) > 4:
            return {"valid": False, "errors": ["Pokemon can only have 4 moves maximum"]}
        
        # Remove None values and duplicates
        move_ids = list(set([mid for mid in move_ids if mid is not None]))
        
        available_moves = self.get_pokemon_available_moves(pokemon_id, level)
        available_move_ids = {move['move_id'] for move in available_moves}
        
        errors = []
        for move_id in move_ids:
            if move_id not in available_move_ids:
                move_name = self.get_move_name(move_id)
                errors.append(f"Pokemon cannot learn {move_name} at level {level}")
        
        return {"valid": len(errors) == 0, "errors": errors}

    def get_move_name(self, move_id: int) -> str:
        """Get move name by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT name FROM Moves WHERE id = ?", (move_id,))
            result = cursor.fetchone()
            return result[0] if result else f"Move #{move_id}"

    def get_move_details(self, move_id: int) -> Optional[dict]:
        """Get detailed information about a move"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, name, type, power, accuracy, pp, effect
                FROM Moves WHERE id = ?
            """, (move_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'name': row['name'],
                    'type': row['type'],
                    'power': row['power'],
                    'accuracy': row['accuracy'],
                    'pp': row['pp'],
                    'effect_description': row['effect']
                }
            return None

    def update_team_pokemon_moves(self, tp_id: int, move_ids: List[int]) -> bool:
        """Update moves for a TeamPokemon"""
        # Pad move_ids to have exactly 4 elements (with None for empty slots)
        while len(move_ids) < 4:
            move_ids.append(None)
        move_ids = move_ids[:4]  # Ensure max 4 moves
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE TeamPokemon 
                SET move1_id = ?, move2_id = ?, move3_id = ?, move4_id = ?
                WHERE id = ?
            """, (move_ids[0], move_ids[1], move_ids[2], move_ids[3], tp_id))
            conn.commit()
            return conn.total_changes > 0
