CREATE TABLE words
(
    word_ID   TEXT PRIMARY KEY NOT NULL,
    last_time REAL,
    attempts  INTEGER NOT NULL,
    guess     INTEGER NOT NULL
);

CREATE TABLE means
(
    word_ID TEXT NOT NULL REFERENCES words(word_ID),
    mean_ID TEXT NOT NULL,
    PRIMARY KEY (word_ID, mean_ID)
);

CREATE TABLE sessions
(
    time_ID  REAL PRIMARY KEY NOT NULL,
    attempts INTEGER NOT NULL,
    guess    INTEGER NOT NULL
);

CREATE TABLE configs
(
    conf_ID TEXT PRIMARY KEY NOT NULL,
    value   TEXT NOT NULL
);
