CREATE TABLE Movies (
    movie_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    release_year VARCHAR(4),
    genre VARCHAR(100),
    description TEXT
);

CREATE TABLE Movie_Embeddings (
    movie_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    release_year VARCHAR(4),
    genre VARCHAR(100),
    description TEXT,
    embeddings vector(324)
);

