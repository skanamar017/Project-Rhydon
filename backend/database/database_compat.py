"""
Simplified database module that imports from the new modular structure.
This file is kept for backward compatibility but delegates to the new modules.
"""

# Import from the new modular structure
from models import Team, TeamPokemon, PokemonStats, Gen1StatCalculator
from database_service import PokemonDatabase
from move_service import MoveService

# Re-export everything for backward compatibility
__all__ = [
    'Team', 'TeamPokemon', 'PokemonStats', 'Gen1StatCalculator',
    'PokemonDatabase', 'MoveService'
]
