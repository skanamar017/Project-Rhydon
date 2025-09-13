--change trainrs to have more detail
--add gym members



CREATE TABLE PokemonType
(
    type_name VARCHAR(20) PRIMARY KEY
);

INSERT INTO PokemonType
    (type_name)
VALUES
    ('Normal'),
    ('Fire'),
    ('Water'),
    ('Grass'),
    ('Electric'),
    ('Ice'),
    (50)
NOT NULL,
('Poison'),
(20) NOT NULL,
('Flying'),
(20),
('Bug'),
(base_hp >= 0),
('Ghost'),
(base_attack >= 0),

(base_defense >= 0),
    id INTEGER PRIMARY KEY AUTOINCREMENT,
(base_special >= 0),
    name VARCHAR
(base_speed >= 0),
    type1 VARCHAR
(255),
    type2 VARCHAR
(type1) REFERENCES PokemonType
(type_name),
(base_hp >= 0),
(type2) REFERENCES PokemonType
(type_name)
        );
(base_defense >= 0),
    base_special INT NOT NULL CHECK
(base_special >= 0),
    base_speed INT NOT NULL CHECK
(base_speed >= 0),
    entry VARCHAR
(255),
    FOREIGN KEY
(type1) REFERENCES PokemonType
(50) NOT NULL,
    FOREIGN KEY
(20) NOT NULL,
(type_name)
);
(accuracy >= 0 AND accuracy <= 100),
CREATE TABLE Moves (
(pp > 0),
    name VARCHAR
(255),
    type VARCHAR
(type) REFERENCES PokemonType
(type_name)
    );
(accuracy >= 0 AND accuracy <= 100),
    pp INT CHECK
(pp > 0),
    effect VARCHAR
(255),
    FOREIGN KEY
(type) REFERENCES PokemonType
(type_name)
);

CREATE TABLE PokemonMoves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pokemon_id INT NOT NULL,
    move_id INT NOT NULL,
    level_learned INT,
    pp INT CHECK
(pp > 0),
    FOREIGN KEY
(pokemon_id) REFERENCES Pokemon
(id),
    FOREIGN KEY
(move_id) REFERENCES Moves
(id)
);

(pp > 0),
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
(pokemon_id) REFERENCES Pokemon
(id),
-- );
(move_id) REFERENCES Moves
(id)
    );
CREATE TABLE PartyPokemon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pokemon_id INT NOT NULL,
    nickname VARCHAR
(50),
    level INT CHECK
(level BETWEEN 1 AND 100),
    iv_attack INT CHECK
(iv_attack BETWEEN 0 AND 15),
    iv_defense INT CHECK
(iv_defense BETWEEN 0 AND 15),
    iv_speed INT CHECK
(iv_speed BETWEEN 0 AND 15),
    iv_special INT CHECK
(iv_special BETWEEN 0 AND 15),
    ev_hp INT DEFAULT 0 CHECK
(ev_hp BETWEEN 0 AND 65535),
    ev_attack INT DEFAULT 0 CHECK
(ev_attack BETWEEN 0 AND 65535),
    ev_defense INT DEFAULT 0 CHECK
(ev_defense BETWEEN 0 AND 65535),
    ev_speed INT DEFAULT 0 CHECK
(ev_speed BETWEEN 0 AND 65535),
    ev_special INT DEFAULT 0 CHECK
(ev_special BETWEEN 0 AND 65535),
    current_hp INT,
    status VARCHAR
(20),
    move1_id INT,
    move2_id INT,
    move3_id INT,
    move4_id INT,
    FOREIGN KEY
(pokemon_id) REFERENCES Pokemon
(pokedex_number),
    FOREIGN KEY
(move1_id) REFERENCES Moves
(id),
    FOREIGN KEY
(move2_id) REFERENCES Moves
(id),
    FOREIGN KEY
(move3_id) REFERENCES Moves
(id),
    FOREIGN KEY
(move4_id) REFERENCES Moves
(id)
);



-- Create Evolution table to track Pokemon evolution chains
CREATE TABLE
IF NOT EXISTS Evolution
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_pokemon_id INTEGER NOT NULL,
    to_pokemon_id INTEGER NOT NULL,
    evolution_method TEXT,
    minimum_level INTEGER,
    evolution_item TEXT,
    trade_required BOOLEAN DEFAULT FALSE,
    FOREIGN KEY
(from_pokemon_id) REFERENCES Pokemon
(pokedex_number),
    FOREIGN KEY
(to_pokemon_id) REFERENCES Pokemon
(pokedex_number),
    UNIQUE
(from_pokemon_id, to_pokemon_id)
);

-- Index for faster lookups
CREATE INDEX
IF NOT EXISTS idx_evolution_from ON Evolution
(from_pokemon_id);
CREATE INDEX
IF NOT EXISTS idx_evolution_to ON Evolution
(to_pokemon_id);
