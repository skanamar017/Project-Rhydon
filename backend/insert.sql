-- remove Fairy typing and replace with gen 1 typing
-- Sample Data for Pokemon Table
-- Format: ('Name', 'Type1', 'Type2', HP, Attack, Defense, Special, Speed)

INSERT INTO Trainers
    (name, age, gender, occupation)
VALUES
    ('Ash', 10, 'Male', 'Pokemon Trainer'),
    ('Misty', 12, 'Female', 'Gym Leader'),
    ('Brock', 15, 'Male', 'Gym Leader'),
    ('Lt. Surge', 35, 'Male', 'Gym Leader'),
    ('Erika', 18, 'Female', 'Gym Leader'),
    ('Koga', 32, 'Male', 'Gym Leader'),
    ('Sabrina', 21, 'Female', 'Gym Leader'),
    ('Blaine', 50, 'Male', 'Gym Leader'),
    ('Giovanni', 45, 'Male', 'Team Rocket Boss'),
    ('Lorelei', 30, 'Female', 'Ice Elite Four');

INSERT INTO TrainerPokemon
    (trainer_id, pokemon_id, nickname, level, iv_attack, iv_defense, iv_speed, iv_special, ev_hp, ev_attack, ev_defense, ev_speed, ev_special)
VALUES
    -- Ash's Pokémon
    (1, 25, 'Sparky', 10, 15, 12, 14, 13, 0, 0, 0, 0, 0),
    -- Pikachu
    (1, 1, 'Leafy', 8, 10, 11, 8, 12, 0, 0, 0, 0, 0),
    -- Bulbasaur
    (1, 4, 'Flare', 9, 12, 9, 13, 11, 0, 0, 0, 0, 0),
    -- Charmander
    (1, 7, 'Bubbles', 8, 8, 14, 10, 9, 0, 0, 0, 0, 0),
    -- Squirtle

    -- Misty's Pokémon
    (2, 120, 'Sting', 12, 11, 10, 15, 12, 0, 0, 0, 0, 0),
    -- Staryu
    (2, 121, 'Shelly', 14, 13, 12, 14, 15, 0, 0, 0, 0, 0),
    -- Starmie
    (2, 54, 'Quackers', 10, 9, 8, 7, 11, 0, 0, 0, 0, 0),
    -- Psyduck

    -- Brock's Pokémon
    (3, 95, 'Onixy', 15, 8, 15, 6, 5, 0, 0, 0, 0, 0),
    -- Onix
    (3, 74, 'Rocky', 12, 14, 13, 4, 6, 0, 0, 0, 0, 0),
    -- Geodude
    (3, 41, 'Zubats', 10, 9, 7, 11, 8, 0, 0, 0, 0, 0),
    -- Zubat

    -- Lt. Surge's Pokémon
    (4, 26, 'Bolt', 20, 15, 10, 15, 12, 0, 0, 0, 0, 0),
    -- Raichu
    (4, 25, 'Sparky Jr.', 18, 14, 8, 13, 11, 0, 0, 0, 0, 0),
    -- Pikachu

    -- Erika's Pokémon
    (5, 71, 'Vile', 16, 12, 11, 13, 15, 0, 0, 0, 0, 0),
    -- Victreebel
    (5, 43, 'Oddy', 14, 8, 9, 6, 12, 0, 0, 0, 0, 0),
    -- Oddish

    -- Koga's Pokémon
    (6, 110, 'Weezy', 17, 13, 14, 9, 12, 0, 0, 0, 0, 0),
    -- Weezing
    (6, 89, 'Muk', 18, 15, 11, 7, 10, 0, 0, 0, 0, 0),
    -- Muk
    (6, 48, 'Venonat', 12, 7, 8, 9, 6, 0, 0, 0, 0, 0),
    -- Venonat

    -- Sabrina's Pokémon
    (7, 65, 'Alak', 20, 10, 8, 15, 15, 0, 0, 0, 0, 0),
    -- Alakazam
    (7, 64, 'Kadabra', 18, 9, 7, 14, 14, 0, 0, 0, 0, 0),
    -- Kadabra

    -- Blaine's Pokémon
    (8, 126, 'Magmy', 18, 14, 9, 12, 15, 0, 0, 0, 0, 0),
    -- Magmar
    (8, 77, 'Ponyta', 16, 11, 8, 10, 9, 0, 0, 0, 0, 0),
    -- Ponyta

    -- Giovanni's Pokémon
    (9, 112, 'Rokky', 22, 15, 15, 8, 10, 0, 0, 0, 0, 0),
    -- Rhydon
    (9, 34, 'Nido', 20, 14, 12, 13, 13, 0, 0, 0, 0, 0),
    -- Nidoking

    -- Lorelei's Pokémon
    (10, 121, 'Stary', 18, 12, 13, 15, 14, 0, 0, 0, 0, 0),
    -- Starmie
    (10, 91, 'Cloy', 16, 13, 15, 11, 12, 0, 0, 0, 0, 0);     -- Cloyster
