from yoyo import step


steps = [
   step(
       """
        drop index if exists game_nam;
         create unique index game_nam on games_mater ("Client_id", "Game_id", "rev_id");
        """
   )
]
