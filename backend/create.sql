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
    pokedex_number INT NOT NULL,
    name VARCHAR
(50) NOT NULL,
    type1 VARCHAR
(20) NOT NULL,
    type2 VARCHAR
(20),
    base_hp INT NOT NULL CHECK
(base_hp >= 0),
    base_attack INT NOT NULL CHECK
(base_attack >= 0),
    base_defense INT NOT NULL CHECK
(base_defense >= 0),
    base_special INT NOT NULL CHECK
(base_special >= 0),
    base_speed INT NOT NULL CHECK
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
    power INT,
    accuracy INT CHECK
(accuracy >= 0 AND accuracy <= 100),
    FOREIGN KEY
(type) REFERENCES PokemonType
(type_name)
);

CREATE TABLE PokemonMoves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pokemon_id INT NOT NULL,
    move_id INT NOT NULL,
    level_learned INT,
    FOREIGN KEY
(pokemon_id) REFERENCES Pokemon
(id),
    FOREIGN KEY
(move_id) REFERENCES Moves
(id)
);

CREATE TABLE Trainers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR
(100) NOT NULL,
    age INT CHECK
(age > 0),
    gender VARCHAR
(10) CHECK
(gender IN
('Male', 'Female', 'Other')),
    occupation VARCHAR
(100)
);



CREATE TABLE TrainerPokemon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trainer_id INT NOT NULL,
    pokemon_id INT NOT NULL,
    nickname VARCHAR
(50),
    level INT CHECK
(level BETWEEN 1 AND 100),
    -- Individual Values (IVs) - Generation 1 uses 0-15 range
    -- IVs will be randomly generated when Pokemon is created
    iv_attack INT CHECK
(iv_attack BETWEEN 0 AND 15),
    iv_defense INT CHECK
(iv_defense BETWEEN 0 AND 15),
    iv_speed INT CHECK
(iv_speed BETWEEN 0 AND 15),
    iv_special INT CHECK
(iv_special BETWEEN 0 AND 15),
    -- Note: HP IV is calculated from other IVs in Gen 1
    -- Effort Values (EVs) - Generation 1 uses 0-65535 range
    -- EVs start at 0 and are gained through training
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
    FOREIGN KEY
(trainer_id) REFERENCES Trainers
(id) ON
DELETE CASCADE,
    FOREIGN KEY (pokemon_id)
REFERENCES Pokemon
(id)
);