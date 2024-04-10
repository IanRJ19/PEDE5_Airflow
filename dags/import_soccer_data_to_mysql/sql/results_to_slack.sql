SELECT player_id, name, age, number, position, team_name
FROM dwh.soccer_players
WHERE etl_date = '{{ ds_nodash }}' 