--change trainrs to have more detail
--add gym members

-- Users table for authentication
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR
(50) NOT NULL UNIQUE,
    password_hash VARCHAR
(255) NOT NULL,
    email VARCHAR
(100) UNIQUE
);



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
    ('Fighting'),
    ('Poison'),
    ('Ground'),
    ('Flying'),
    ('Psychic'),
    ('Bug'),
    ('Rock'),
    ('Ghost'),
    ('Dragon');


CREATE TABLE Pokemon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pokedex_number INTEGER NOT NULL UNIQUE,
    name VARCHAR
(50) NOT NULL,
    type1 VARCHAR
(20) NOT NULL,
    type2 VARCHAR
(20),
    base_hp INTEGER NOT NULL CHECK
(base_hp >= 0),
    base_attack INTEGER NOT NULL CHECK
(base_attack >= 0),
    base_defense INTEGER NOT NULL CHECK
(base_defense >= 0),
    base_special INTEGER NOT NULL CHECK
(base_special >= 0),
    base_speed INTEGER NOT NULL CHECK
(base_speed >= 0),
    entry VARCHAR
(255),
    FOREIGN KEY
(type1) REFERENCES PokemonType
(type_name),
    FOREIGN KEY
(type2) REFERENCES PokemonType
(type_name)
);


CREATE TABLE Moves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR
(50) NOT NULL,
    type VARCHAR
(20) NOT NULL,
    power INTEGER,
    accuracy INTEGER CHECK
(accuracy >= 0 AND accuracy <= 100),
    pp INTEGER CHECK
(pp > 0),
    effect VARCHAR
(255),
    FOREIGN KEY
(type) REFERENCES PokemonType
(type_name)
);


CREATE TABLE PokemonMoves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pokemon_id INTEGER NOT NULL,
    move_id INTEGER NOT NULL,
    level_learned INTEGER,
    pp INTEGER CHECK
(pp > 0),
    FOREIGN KEY
(pokemon_id) REFERENCES Pokemon
(id),
    FOREIGN KEY
(move_id) REFERENCES Moves
(id)
);


CREATE TABLE Team (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR
(100) NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY
(user_id) REFERENCES users
(id)
);




CREATE TABLE TeamPokemon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    pokemon_id INTEGER NOT NULL,
    nickname VARCHAR
(50),
    level INTEGER CHECK
(level BETWEEN 1 AND 100),
    iv_attack INTEGER CHECK
(iv_attack BETWEEN 0 AND 15),
    iv_defense INTEGER CHECK
(iv_defense BETWEEN 0 AND 15),
    iv_speed INTEGER CHECK
(iv_speed BETWEEN 0 AND 15),
    iv_special INTEGER CHECK
(iv_special BETWEEN 0 AND 15),
    ev_hp INTEGER DEFAULT 0 CHECK
(ev_hp BETWEEN 0 AND 65535),
    ev_attack INTEGER DEFAULT 0 CHECK
(ev_attack BETWEEN 0 AND 65535),
    ev_defense INTEGER DEFAULT 0 CHECK
(ev_defense BETWEEN 0 AND 65535),
    ev_speed INTEGER DEFAULT 0 CHECK
(ev_speed BETWEEN 0 AND 65535),
    ev_special INTEGER DEFAULT 0 CHECK
(ev_special BETWEEN 0 AND 65535),
    current_hp INTEGER,
    status VARCHAR
(20),
    move1_id INTEGER,
    move2_id INTEGER,
    move3_id INTEGER,
    move4_id INTEGER,
    FOREIGN KEY
(team_id) REFERENCES Team
(id) ON
DELETE CASCADE,
    FOREIGN KEY (pokemon_id)
REFERENCES Pokemon
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
CREATE TABLE Evolution (
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
