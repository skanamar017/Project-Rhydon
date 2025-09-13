#!/bin/bash
# Insert a sample party of 6 PartyPokemon using the API

API_URL="http://localhost:5000/pokemon/"

curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{"pokemon_id": 1, "nickname": "Bulby", "level": 5, "ev_hp": 100, "ev_attack": 100, "ev_defense": 100, "ev_speed": 100, "ev_special": 100}'

echo
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{"pokemon_id": 4, "nickname": "Charmy", "level": 5, "ev_hp": 90, "ev_attack": 110, "ev_defense": 80, "ev_speed": 120, "ev_special": 100}'

echo
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{"pokemon_id": 7, "nickname": "Squirtz", "level": 5, "ev_hp": 120, "ev_attack": 80, "ev_defense": 120, "ev_speed": 80, "ev_special": 90}'

echo
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{"pokemon_id": 25, "nickname": "Pika", "level": 5, "ev_hp": 80, "ev_attack": 120, "ev_defense": 70, "ev_speed": 130, "ev_special": 110}'

echo
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{"pokemon_id": 39, "nickname": "Jiggly", "level": 5, "ev_hp": 150, "ev_attack": 60, "ev_defense": 60, "ev_speed": 60, "ev_special": 80}'

echo
curl -X POST $API_URL \
  -H "Content-Type: application/json" \
  -d '{"pokemon_id": 133, "nickname": "Eevee", "level": 5, "ev_hp": 100, "ev_attack": 100, "ev_defense": 100, "ev_speed": 100, "ev_special": 100}'

echo "Sample party inserted!"
