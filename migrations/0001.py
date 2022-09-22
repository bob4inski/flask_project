from yoyo import step


steps = [
   step(
       """
       create table games
(
    id int generated always as identity primary key ,
    name text,
    developer text,
    genre text

);
create table client
(
    id bigint generated always as identity primary key,
    name text,
    age int
);

create table reviews
(
    id int generated always as identity primary key,
    body text,
    commentator int references client,
    game int references games,
    mark int
);

create table client2game
(
    id_client int references client(id),
    game_id int references games,
    primary key (id_client,game_id)
);
       """
   )
]
