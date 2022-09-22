from yoyo import step


steps = [
   step(
       """
        refresh
        materialized view concurrently games_mater;
        """
   )
]
