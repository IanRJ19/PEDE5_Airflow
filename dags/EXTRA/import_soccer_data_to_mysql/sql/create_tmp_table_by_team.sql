DROP TABLE IF EXISTS {{ params.team_name }}_soccer_players;

CREATE TABLE IF NOT EXISTS {{ params.team_name }}_soccer_players
(
    player_id int,
    name varchar(100),
    age int,
    number int,
    position varchar(100),
    photo varchar(200)
);