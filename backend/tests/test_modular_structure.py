"""
Test script to verify the new modular structure works correctly.
"""

def test_imports():
    """Test that all new modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test models
        from models import Team, TeamPokemon, Gen1StatCalculator
        print("✅ Models imported successfully")
        
        # Test database service
        from database_service import PokemonDatabase
        print("✅ Database service imported successfully")
        
        # Test move service
        from move_service import MoveService
        print("✅ Move service imported successfully")
        
        # Test evolution utils
        from evolution_utils import setup_evolution_system
        print("✅ Evolution utils imported successfully")
        
        # Test compatibility layer
        from database_compat import PokemonDatabase as CompatDB
        print("✅ Compatibility layer imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    try:
        print("\nTesting basic functionality...")
        
        # Test stat calculator
        from models import Gen1StatCalculator
        
        base_stats = {'hp': 78, 'attack': 84, 'defense': 78, 'speed': 100, 'special': 109}
        ivs = {'attack': 15, 'defense': 15, 'speed': 15, 'special': 15}
        evs = {'hp': 0, 'attack': 0, 'defense': 0, 'speed': 0, 'special': 0}
        
        stats = Gen1StatCalculator.calculate_all_stats(base_stats, 50, ivs, evs)
        print(f"✅ Stat calculation works: HP={stats.hp}, Attack={stats.attack}")
        
        # Test random IV generation
        random_ivs = Gen1StatCalculator.generate_random_ivs()
        print(f"✅ Random IV generation works: {random_ivs}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def test_database_connection():
    """Test database connection (if database exists)"""
    try:
        print("\nTesting database connection...")
        
        from database_service import PokemonDatabase
        import os
        
        if os.path.exists("pokemon.db"):
            db = PokemonDatabase()
            teams = db.get_all_teams()
            print(f"✅ Database connection works: {len(teams)} teams found")
            return True
        else:
            print("⚠️  No database found (run complete_database_setup.py first)")
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing New Modular Structure")
    print("=" * 40)
    
    success = True
    success &= test_imports()
    success &= test_basic_functionality()
    success &= test_database_connection()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! New modular structure is working.")
        print("\nNext steps:")
        print("1. Run: python complete_database_setup.py")
        print("2. Run: python app.py")
        print("3. Test API: curl http://localhost:5001/")
    else:
        print("❌ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
