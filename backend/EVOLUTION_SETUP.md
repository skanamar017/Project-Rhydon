# Pokemon Evolution System Setup

## Quick Start

After clearing your database and restarting the application, run this single command to restore the complete evolution system:

```bash
python setup_evolution_system.py
```

## What This Script Does

1. **Creates Evolution Table**: Sets up the database table to store evolution relationships
2. **Fetches Evolution Data**: Downloads accurate Generation 1 evolution data from PokeAPI (72 relationships)
3. **Updates Pokemon Moves**: Adds moves from pre-evolutions to evolved Pokemon (adds ~66 additional moves)

## Results

- **Charizard** will know moves from Charmander and Charmeleon
- **Blastoise** will know moves from Squirtle and Wartortle
- **Venusaur** will know moves from Bulbasaur and Ivysaur
- And so on for all evolved Pokemon!

## Example

Before: Charizard knows 37 moves
After: Charizard knows 100+ moves (including Ember from Charmander, etc.)

## Database Persistence

⚠️ **Important**: If you clear the database, you MUST run this script again to restore the evolution system. The evolution relationships and inherited moves are not part of the base database - they're enhancements added by this script.

## API Usage

After running the setup, use the enhanced API endpoint:

```
GET /Pokemon/{id}/moves/with_evolutions
```

This returns moves from the entire evolution chain with source information.

## Troubleshooting

- Make sure you're in the `backend/` directory when running the script
- Ensure `pokemon.db` exists before running
- The script requires internet access to fetch data from PokeAPI
- Installation may require: `pip install requests`
