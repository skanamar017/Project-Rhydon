"""
Recommended Backend Directory Restructuring
==========================================

This script will help you reorganize your backend into a cleaner structure.
"""

import os
import shutil
from pathlib import Path

def create_new_structure():
    """Create the new directory structure"""
    
    # Define the new structure
    structure = {
        'database/': [
            # Database setup and schema
            'complete_database_setup.py',
            'create.sql',
            'pokemon.db',
            
            # Data files
            'data/gen1_pokemon_inserts.sql',
            'data/gen1_moves_inserts.sql', 
            'data/gen1_pokemon_moves_inserts_corrected.sql',
            
            # Legacy scripts (can be deleted after restructuring)
            'legacy/fetch_gen1_pokemon.py',
            'legacy/fetch_gen1_moves.py',
            'legacy/fetch_gen1_pokemon_moves.py',
            'legacy/fetch_evolution_data.py',
            'legacy/setup_evolution_system.py',
            'legacy/update_pokemon_moves_with_evolutions.py',
            
            # Database services
            'services/database_service.py',
            'services/move_service.py',
            'services/models.py',
            
            # Compatibility
            'database.py',  # Keep for backward compatibility
            'database_compat.py'
        ],
        
        'server/': [
            # Flask application
            'app.py',
            'main_flask.py',  # Keep for backward compatibility
            
            # Routes
            'routes/__init__.py',
            'routes/team_routes.py',
            'routes/pokemon_routes.py', 
            'routes/move_routes.py',
            
            # Utilities
            'utils/evolution_utils.py'
        ],
        
        'tests/': [
            'test_modular_structure.py',
            'check_hp_calculations.py'
        ],
        
        'docs/': [
            'EVOLUTION_SETUP.md',
            'REFACTORING_SUMMARY.md'
        ]
    }
    
    return structure

def print_recommended_structure():
    """Print the recommended new structure"""
    print("🏗️  RECOMMENDED NEW BACKEND STRUCTURE")
    print("=" * 50)
    print()
    print("backend/")
    print("├── database/                      # 🗄️  All database-related files")
    print("│   ├── complete_database_setup.py # Complete DB setup script")
    print("│   ├── pokemon.db                 # SQLite database")
    print("│   ├── create.sql                 # Database schema")
    print("│   ├── data/                      # SQL data files")
    print("│   │   ├── gen1_pokemon_inserts.sql")
    print("│   │   ├── gen1_moves_inserts.sql")
    print("│   │   └── gen1_pokemon_moves_inserts_corrected.sql")
    print("│   ├── services/                  # Database service layer")
    print("│   │   ├── database_service.py    # Core DB operations")
    print("│   │   ├── move_service.py        # Move-related operations")
    print("│   │   └── models.py              # Data models")
    print("│   ├── legacy/                    # Old scripts (can delete)")
    print("│   │   ├── fetch_gen1_*.py")
    print("│   │   ├── setup_evolution_system.py")
    print("│   │   └── update_pokemon_moves_with_evolutions.py")
    print("│   ├── database.py                # Backward compatibility")
    print("│   └── database_compat.py         # Compatibility layer")
    print("│")
    print("├── server/                        # 🌐 Flask server files")
    print("│   ├── app.py                     # New modular Flask app")
    print("│   ├── main_flask.py              # Original Flask app (legacy)")
    print("│   ├── routes/                    # Route handlers")
    print("│   │   ├── __init__.py")
    print("│   │   ├── team_routes.py")
    print("│   │   ├── pokemon_routes.py")
    print("│   │   └── move_routes.py")
    print("│   └── utils/")
    print("│       └── evolution_utils.py     # Evolution utilities")
    print("│")
    print("├── tests/                         # 🧪 Testing files")
    print("│   ├── test_modular_structure.py")
    print("│   └── check_hp_calculations.py")
    print("│")
    print("└── docs/                          # 📋 Documentation")
    print("    ├── EVOLUTION_SETUP.md")
    print("    └── REFACTORING_SUMMARY.md")
    print()
    
def create_migration_script():
    """Create a script to migrate to the new structure"""
    
    migration_commands = """#!/bin/bash
# Migration script to reorganize backend directory structure

echo "🚀 Starting backend directory restructuring..."

# Create new directories
mkdir -p database/data database/services database/legacy
mkdir -p server/routes server/utils  
mkdir -p tests docs

echo "📁 Created new directory structure"

# Move database-related files
echo "🗄️  Moving database files..."

# Core database files
mv complete_database_setup.py database/
mv create.sql database/
mv pokemon.db database/ 2>/dev/null || echo "  pokemon.db not found (will be created by setup)"

# Data files
mv gen1_pokemon_inserts.sql database/data/
mv gen1_moves_inserts.sql database/data/
mv gen1_pokemon_moves_inserts_corrected.sql database/data/

# Legacy scripts
mv fetch_gen1_*.py database/legacy/
mv fetch_evolution_data.py database/legacy/
mv setup_evolution_system.py database/legacy/
mv update_pokemon_moves_with_evolutions.py database/legacy/

# Database services
mv database_service.py database/services/
mv move_service.py database/services/
mv models.py database/services/

# Compatibility files
mv database.py database/
mv database_compat.py database/

echo "🌐 Moving server files..."

# Server files
mv app.py server/
mv main_flask.py server/
mv evolution_utils.py server/utils/

# Routes (if they exist)
if [ -d "routes" ]; then
    mv routes/* server/routes/
    rmdir routes
fi

echo "🧪 Moving test files..."
mv test_modular_structure.py tests/
mv check_hp_calculations.py tests/

echo "📋 Moving documentation..."
mv EVOLUTION_SETUP.md docs/
mv REFACTORING_SUMMARY.md docs/

echo "✅ Migration complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update import paths in your files"
echo "2. Test the new structure: cd tests && python test_modular_structure.py"
echo "3. Run database setup: cd database && python complete_database_setup.py"
echo "4. Start server: cd server && python app.py"
"""
    
    with open('/Users/sai/Documents/Projects/tenth-week/Project-Rhydon/backend/migrate_structure.sh', 'w') as f:
        f.write(migration_commands)
    
    os.chmod('/Users/sai/Documents/Projects/tenth-week/Project-Rhydon/backend/migrate_structure.sh', 0o755)
    
    print("📝 Created migration script: migrate_structure.sh")

def main():
    """Main function"""
    print_recommended_structure()
    
    print("💡 BENEFITS OF NEW STRUCTURE:")
    print("=" * 50)
    print("✅ Clear separation of database vs server concerns")
    print("✅ Easier to find and maintain files")
    print("✅ Better for team collaboration")
    print("✅ Follows standard project organization patterns")
    print("✅ Legacy files preserved but organized")
    print("✅ Easy to understand what each directory does")
    print()
    
    print("🔧 TO IMPLEMENT THIS STRUCTURE:")
    print("=" * 50)
    print("Option 1: I can create a migration script for you")
    print("Option 2: You can manually move files following the structure above")
    print("Option 3: Keep current structure (it works fine too)")
    print()
    
    create_migration_script()
    
    print("🚨 IMPORTANT AFTER MIGRATION:")
    print("=" * 50)
    print("You'll need to update import paths:")
    print()
    print("# Old imports:")
    print("from database_service import PokemonDatabase")
    print("from models import Team, TeamPokemon")
    print()
    print("# New imports:")
    print("from database.services.database_service import PokemonDatabase")
    print("from database.services.models import Team, TeamPokemon")
    print()
    print("Or create __init__.py files to simplify imports!")

if __name__ == "__main__":
    main()
