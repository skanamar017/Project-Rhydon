#!/bin/bash
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
mv insert.sql database/data/

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
