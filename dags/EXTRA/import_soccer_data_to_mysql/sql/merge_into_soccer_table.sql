DELETE FROM soccer_players
WHERE team_name = '{{ params.team_name }}'
AND etl_date = '{{ ds_nodash }}'
;

INSERT INTO soccer_players
(
    player_id,
    name,
    age,
    number,
    position,
    photo,
    team_name,
    etl_date
)
SELECT 
    player_id,
    name,
    age,
    number,
    position,
    photo,
    '{{ params.team_name }}',
    '{{ ds_nodash }}'
FROM {{ params.team_name }}_soccer_players;