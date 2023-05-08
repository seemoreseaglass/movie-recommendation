--BEGIN　TRANSACTION

--ATTACH DATABASE '/workspaces/95611923/movies/movies.db' as X;

----CREATE TABLE main.movies(id INTEGER, title TEXT NOT NULL, year NUMERIC, PRIMARY KEY(id));
INSERT OR REPLACE INTO main.movies SELECT * FROM X.movies;

----CREATE TABLE main.people(id INTEGER, name TEXT NOT NULL, birth NUMERIC, PRIMARY KEY(id));
INSERT OR REPLACE INTO main.people SELECT * FROM X.people;

--CREATE TABLE main.stars(movie_id INTEGER NOT NULL, person_id INTEGER NOT NULL, FOREIGN KEY(movie_id) REFERENCES movies(id), FOREIGN KEY(person_id) REFERENCES people(id));
INSERT OR REPLACE INTO main.stars SELECT * FROM X.stars;

--CREATE TABLE main.directors(movie_id INTEGER NOT NULL, person_id INTEGER NOT NULL, FOREIGN KEY(movie_id) REFERENCES movies(id), FOREIGN KEY(person_id) REFERENCES people(id));
INSERT OR REPLACE INTO main.directors SELECT * FROM X.directors;

--CREATE TABLE main.ratings(movie_id INTEGER NOT NULL, rating REAL NOT NULL, votes INTEGER NOT NULL, FOREIGN KEY(movie_id) REFERENCES movies(id));
INSERT OR REPLACE INTO main.ratings SELECT * FROM X.ratings;

--CREATE INDEX movie_index ON movies(id);
--CREATE INDEX person_index ON people(id);

DETACH DATABASE X;

--COMMIT;