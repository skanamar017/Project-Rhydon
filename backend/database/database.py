"""
Simplified database module that imports from the new modular structure.
This file is kept for backward compatibility but delegates to the new modules.
"""

import sqlite3
import os
from typing import Optional, List

# Import from the new modular structure
from .services.models import Team, TeamPokemon, PokemonStats, Gen1StatCalculator
from .services.database_service import PokemonDatabase as ServicePokemonDatabase
from .services.move_service import MoveService

# Re-export everything for backward compatibility
__all__ = [
    'Team', 'TeamPokemon', 'PokemonStats', 'Gen1StatCalculator',
    'PokemonDatabase', 'MoveService'
]

# Use the service class directly for backward compatibility
PokemonDatabase = ServicePokemonDatabase