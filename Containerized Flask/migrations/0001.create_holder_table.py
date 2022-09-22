from yoyo import step


steps = [
   step(
       """
       create table holder
        (
            phone text primary key,
            name  text not null
        );
       """
   )
]