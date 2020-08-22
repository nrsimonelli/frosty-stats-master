CREATE TABLE players (
	id SERIAL PRIMARY KEY,
	name VARCHAR(50)
);


CREATE TABLE games (
	id SERIAL PRIMARY KEY,
	t1_player1 INT REFERENCES players,
	t1_player2 INT REFERENCES players,
	t1_player3 INT REFERENCES players,
	t1_player4 INT REFERENCES players,
	t1_player5 INT REFERENCES players,
	t2_player1 INT REFERENCES players,
	t2_player2 INT REFERENCES players,
	t2_player3 INT REFERENCES players,
	t2_player4 INT REFERENCES players,
	t2_player5 INT REFERENCES players,
	t1_score INT,
	t2_score INT,
	tiebreaker INT
);

INSERT INTO players (name) 
VALUES 
('Jagt'),
('Ethan'),
('KJ'),
('Charlie'),
('Charles'),
('Simo'),
('Beef'),
('Trevor'),
('Ryan'),
('Connor');


SELECT * FROM players;
SELECT * FROM games;

COPY games (id, t1_player1, t1_player2, t1_player3, t1_player4, t2_player1, t2_player2, t2_player3, t2_player4, t1_score, t2_score, tiebreaker)
FROM '/Users/joy/prime/tier3/frosty-stats-master/mini_data copy.csv'
DELIMITER ','
CSV HEADER;

FROM 'C:\sampledb\persons.csv'
DELIMITER ','
CSV HEADER;