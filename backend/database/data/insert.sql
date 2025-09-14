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
    (1, 25, 'Pikachu', 50, 3, 7, 12, 0, 0, 0, 0, 0, 0, 120, 'Healthy', 85, 98, 104, 97),
    -- Thunderbolt, Quick Attack, Thunder, Double Team
    (1, 3, 'Bulbasaur', 45, 8, 2, 15, 10, 0, 0, 0, 0, 0, 130, 'Healthy', 75, 73, 22, 77),
    -- Razor Leaf, Sleep Powder, Leech Seed, SolarBeam
    (1, 6, 'Charizard', 55, 1, 14, 6, 11, 0, 0, 0, 0, 0, 150, 'Healthy', 53, 126, 163, 241),
    -- Flamethrower, Fly, Slash, Earthquake
    (1, 9, 'Squirtle', 43, 13, 2, 7, 4, 0, 0, 0, 0, 0, 110, 'Healthy', 57, 58, 59, 127),
    -- Surf, Ice Beam, Bite, Skull Bash

    (2, 121, 'Starmie', 55, 6, 10, 1, 8, 0, 0, 0, 0, 0, 140, 'Healthy', 58, 62, 105, 94),
    -- Surf, Psychic, Thunderbolt, Ice Beam
    (2, 120, 'Staryu', 48, 11, 0, 14, 2, 0, 0, 0, 0, 0, 110, 'Healthy', 58, 62, 61, 105),
    -- Surf, Psychic, Thunderbolt, Recover
    (2, 54, 'Psyduck', 44, 7, 13, 5, 9, 0, 0, 0, 0, 0, 100, 'Healthy', 58, 50, 133, 60),
    -- Surf, Confusion, Disable, Screech
    (2, 55, 'Golduck', 52, 4, 12, 3, 7, 0, 0, 0, 0, 0, 130, 'Healthy', 58, 62, 133, 94),
    -- Surf, Psychic, Screech, Ice Beam

    (3, 95, 'Onix', 50, 2, 11, 8, 13, 0, 0, 0, 0, 0, 120, 'Healthy', 89, 157, 36, 38),
    -- Rock Slide, Earthquake, Bind, Screech
    (3, 76, 'Golem', 54, 9, 5, 0, 6, 0, 0, 0, 0, 0, 140, 'Healthy', 89, 157, 153, 36),
    -- Rock Slide, Earthquake, Explosion, Bind
    (3, 74, 'Geodude', 44, 1, 12, 3, 10, 0, 0, 0, 0, 0, 100, 'Healthy', 89, 157, 153, 36),
    -- Rock Slide, Earthquake, Explosion, Bind
    (3, 42, 'Golbat', 46, 8, 6, 11, 15, 0, 0, 0, 0, 0, 110, 'Healthy', 103, 114, 44, 17),
    -- Wing Attack, Bite, Confuse Ray, Toxic

    (4, 26, 'Raichu', 56, 0, 13, 2, 14, 0, 0, 0, 0, 0, 130, 'Healthy', 85, 98, 104, 97),
    -- Thunderbolt, Quick Attack, Thunder, Double Team
    (4, 100, 'Electrode', 52, 6, 11, 8, 1, 0, 0, 0, 0, 0, 110, 'Healthy', 85, 97, 120, 49),
    -- Thunderbolt, Double Team, Explosion, Swift
    (4, 82, 'Magneton', 50, 3, 7, 12, 0, 0, 0, 0, 0, 0, 120, 'Healthy', 85, 97, 49, 63),
    -- Thunderbolt, Double Team, Swift, Thunder Wave

    (5, 71, 'Victreebel', 54, 10, 4, 13, 7, 0, 0, 0, 0, 0, 140, 'Healthy', 75, 73, 22, 77),
    -- Razor Leaf, Sleep Powder, Leech Seed, SolarBeam
    (5, 45, 'Vileplume', 52, 2, 8, 6, 12, 0, 0, 0, 0, 0, 130, 'Healthy', 80, 73, 77, 22),
    -- Petal Dance, Sleep Powder, SolarBeam, Leech Seed
    (5, 114, 'Tangela', 48, 5, 9, 11, 3, 0, 0, 0, 0, 0, 120, 'Healthy', 22, 77, 73, 21),
    -- Leech Seed, SolarBeam, Sleep Powder, Bind

    (6, 110, 'Weezing', 56, 14, 0, 7, 13, 0, 0, 0, 0, 0, 140, 'Healthy', 124, 120, 92, 53),
    -- Sludge, Explosion, Smokescreen, Toxic
    (6, 89, 'Muk', 54, 11, 2, 15, 8, 0, 0, 0, 0, 0, 130, 'Healthy', 124, 120, 92, 53),
    -- Sludge, Explosion, Smokescreen, Toxic
    (6, 49, 'Venomoth', 50, 6, 12, 0, 4, 0, 0, 0, 0, 0, 120, 'Healthy', 93, 92, 60, 94),
    -- Psychic, Toxic, Stun Spore, Sleep Powder

    (7, 65, 'Alakazam', 60, 13, 1, 5, 9, 0, 0, 0, 0, 0, 150, 'Healthy', 94, 105, 93, 60),
    -- Psychic, Recover, Reflect, Thunder Wave
    (7, 122, 'Mr. Mime', 54, 7, 4, 11, 2, 0, 0, 0, 0, 0, 120, 'Healthy', 93, 60, 105, 94),
    -- Psychic, Thunder Wave, Reflect, Barrier
    (7, 49, 'Venomoth', 52, 8, 13, 6, 10, 0, 0, 0, 0, 0, 110, 'Healthy', 93, 92, 60, 94),
    -- Psychic, Toxic, Stun Spore, Sleep Powder


    (8, 126, 'Magmar', 58, 2, 11, 8, 1, 0, 0, 0, 0, 0, 140, 'Healthy', 53, 126, 241, 126),
    -- Flamethrower, Fire Punch, Hyper Beam, Confuse Ray
    (8, 78, 'Rapidash', 54, 10, 4, 13, 7, 0, 0, 0, 0, 0, 130, 'Healthy', 53, 126, 241, 36),
    -- Flamethrower, Fire Spin, Hyper Beam, Stomp
    (8, 59, 'Arcanine', 60, 2, 8, 6, 12, 0, 0, 0, 0, 0, 150, 'Healthy', 53, 126, 241, 36),
    -- Flamethrower, Fire Blast, Hyper Beam, Take Down

    (9, 112, 'Rhydon', 60, 5, 9, 11, 3, 0, 0, 0, 0, 0, 160, 'Healthy', 157, 89, 36, 38),
    -- Earthquake, Rock Slide, Stomp, Tail Whip
    (9, 31, 'Nidoqueen', 56, 14, 0, 7, 13, 0, 0, 0, 0, 0, 140, 'Healthy', 157, 89, 36, 38),
    -- Earthquake, Rock Slide, Body Slam, Tail Whip   
    (9, 34, 'Nidoking', 58, 11, 2, 15, 8, 0, 0, 0, 0, 0, 145, 'Healthy', 157, 89, 36, 38),
    -- Earthquake, Rock Slide, Body Slam, Tail Whip

    (10, 131, 'Lapras', 56, 7, 4, 11, 15, 0, 0, 0, 0, 0, 150, 'Healthy', 58, 62, 105, 94),
    -- Surf, Psychic, Ice Beam, Thunderbolt
    (10, 91, 'Cloyster', 54, 8, 13, 6, 10, 0, 0, 0, 0, 0, 130, 'Healthy', 58, 105, 120, 49),
    -- Surf, Ice Beam, Explosion, Spike Cannon
    (10, 87, 'Dewgong', 52, 13, 1, 5, 9, 0, 0, 0, 0, 0, 120, 'Healthy', 58, 105, 62, 94),
    -- Surf, Ice Beam, Psychic, Rest
    (10, 124, 'Jynx', 50, 4, 12, 0, 14, 0, 0, 0, 0, 0, 110, 'Healthy', 94, 105, 93, 60); -- Psychic, Ice Beam, Lovely Kiss, Rest