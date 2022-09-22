from yoyo import step


steps = [
   step(
       """
       DROP MATERIALIZED VIEW if exists games_mater;


       create
materialized view games_mater as
select games.name as "Gamename", games.id as "Game_id",developer as "GameDev", "genre",reviews.id as "rev_id",reviews.body as "Review", reviews.mark as "rev_mark", c.name as "Cient Name", c.id as "Client_id"
            from games
            left join reviews on "game" = games.id
            left join client2game  c2g on games.id = c2g.game_id
            left join client c on c.id = c2g.id_client;
        """
   )
]
