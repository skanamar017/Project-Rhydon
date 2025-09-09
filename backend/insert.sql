-- remove Fairy typing and replace with gen 1 typing
-- Sample Data for Pokemon Table
-- Format: ('Name', 'Type1', 'Type2', HP, Attack, Defense, Special, Speed)

INSERT INTO Team
    (name)
VALUES
    ('Ash'),
    ('Misty'),
    ('Brock'),
    ('Lt. Surge'),
    ('Erika'),
    ('Koga'),
    ('Sabrina'),
    ('Blaine'),
    ('Giovanni'),
    ('Lorelei');

INSERT INTO TeamPokemon
    (team_id, pokemon_id, nickname, level, iv_attack, iv_defense, iv_speed, iv_special, ev_hp, ev_attack, ev_defense, ev_speed, ev_special, current_hp, status, move1_id, move2_id, move3_id, move4_id)
VALUES
    -- Ash's Pokémon
    (1, 25, 'Sparky', 10, 15, 12, 14, 13, 0, 0, 0, 0, 0, 35, 'Healthy', NULL, NULL, NULL, NULL),
    -- Pikachu (Thunder Punch)
    (1, 1, 'Leafy', 8, 10, 11, 8, 12, 0, 0, 0, 0, 0, 45, 'Healthy', NULL, NULL, NULL, NULL),
    -- Bulbasaur (Pound)
    (1, 4, 'Flare', 9, 12, 9, 13, 11, 0, 0, 0, 0, 0, 39, 'Healthy', NULL, NULL, NULL, NULL),
    -- Charmander (Fire Punch)
    (1, 7, 'Bubbles', 8, 8, 14, 10, 9, 0, 0, 0, 0, 0, 44, 'Healthy', NULL, NULL, NULL, NULL),
    -- Squirtle (Pound)

    -- Misty's Pokémon
    (2, 120, 'Sting', 12, 11, 10, 15, 12, 0, 0, 0, 0, 0, 30, 'Healthy', NULL, NULL, NULL, NULL),
    -- Staryu (Pound)
    (2, 121, 'Shelly', 14, 13, 12, 14, 15, 0, 0, 0, 0, 0, 60, 'Healthy', NULL, NULL, NULL, NULL),
    -- Starmie (Pound)
    (2, 54, 'Quackers', 10, 9, 8, 7, 11, 0, 0, 0, 0, 0, 50, 'Healthy', NULL, NULL, NULL, NULL),
    -- Psyduck (Pound)

    -- Brock's Pokémon
    (3, 95, 'Onixy', 15, 8, 15, 6, 5, 0, 0, 0, 0, 0, 35, 'Healthy', NULL, NULL, NULL, NULL),
    -- Onix (Pound)
    (3, 74, 'Rocky', 12, 14, 13, 4, 6, 0, 0, 0, 0, 0, 40, 'Healthy', NULL, NULL, NULL, NULL),
    -- Geodude (Pound)
    (3, 41, 'Zubats', 10, 9, 7, 11, 8, 0, 0, 0, 0, 0, 40, 'Healthy', NULL, NULL, NULL, NULL),
    -- Zubat (Gust)

    -- Lt. Surge's Pokémon
    (4, 26, 'Bolt', 20, 15, 10, 15, 12, 0, 0, 0, 0, 0, 60, 'Healthy', NULL, NULL, NULL, NULL),
    -- Raichu (Thunder Punch)
    (4, 25, 'Sparky Jr.', 18, 14, 8, 13, 11, 0, 0, 0, 0, 0, 35, 'Healthy', NULL, NULL, NULL, NULL),
    -- Pikachu (Thunder Punch)

    -- Erika's Pokémon
    (5, 71, 'Vile', 16, 12, 11, 13, 15, 0, 0, 0, 0, 0, 80, 'Healthy', NULL, NULL, NULL, NULL),
    -- Victreebel (Pound)
    (5, 43, 'Oddy', 14, 8, 9, 6, 12, 0, 0, 0, 0, 0, 45, 'Healthy', NULL, NULL, NULL, NULL),
    -- Oddish (Pound)

    -- Koga's Pokémon
    (6, 110, 'Weezy', 17, 13, 14, 9, 12, 0, 0, 0, 0, 0, 65, 'Healthy', NULL, NULL, NULL, NULL),
    -- Weezing (Pound)
    (6, 89, 'Muk', 18, 15, 11, 7, 10, 0, 0, 0, 0, 0, 105, 'Healthy', NULL, NULL, NULL, NULL),
    -- Muk (Pound)
    (6, 48, 'Venonat', 12, 7, 8, 9, 6, 0, 0, 0, 0, 0, 60, 'Healthy', NULL, NULL, NULL, NULL),
    -- Venonat (Pound)

    -- Sabrina's Pokémon
    (7, 65, 'Alak', 20, 10, 8, 15, 15, 0, 0, 0, 0, 0, 55, 'Healthy', NULL, NULL, NULL, NULL),
    -- Alakazam (Pound)
    (7, 64, 'Kadabra', 18, 9, 7, 14, 14, 0, 0, 0, 0, 0, 40, 'Healthy', NULL, NULL, NULL, NULL),
    -- Kadabra (Pound)

    -- Blaine's Pokémon
    (8, 126, 'Magmy', 18, 14, 9, 12, 15, 0, 0, 0, 0, 0, 65, 'Healthy', NULL, NULL, NULL, NULL),
    -- Magmar (Fire Punch)
    (8, 77, 'Ponyta', 16, 11, 8, 10, 9, 0, 0, 0, 0, 0, 50, 'Healthy', NULL, NULL, NULL, NULL),
    -- Ponyta (Fire Punch)

    -- Giovanni's Pokémon
    (9, 112, 'Rokky', 22, 15, 15, 8, 10, 0, 0, 0, 0, 0, 105, 'Healthy', 1, NULL, NULL, NULL),
    -- Rhydon (Pound)
    (9, 34, 'Nido', 20, 14, 12, 13, 13, 0, 0, 0, 0, 0, 81, 'Healthy', 1, NULL, NULL, NULL),
    -- Nidoking (Pound)

    -- Lorelei's Pokémon
    (10, 121, 'Stary', 18, 12, 13, 15, 14, 0, 0, 0, 0, 0, 60, 'Healthy', 8, NULL, NULL, NULL),
    -- Starmie (Ice Punch)
    (10, 91, 'Cloy', 16, 13, 15, 11, 12, 0, 0, 0, 0, 0, 50, 'Healthy', 8, NULL, NULL, NULL);     -- Cloyster (Ice Punch)
