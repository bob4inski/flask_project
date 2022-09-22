drop table if exists client cascade;
drop table if exists games cascade;
drop table if exists reviews cascade;
drop table if exists client2game cascade;




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
    name text
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

insert into games(name, developer, genre)
values ('Forza','ea games','racing'),
       ('wot','lartoshla','arcade'),
       ('maincampf','maicrosoft','aboba'),
       ('call of duty','idn','wars');

insert into client(name)
values ('robert'),
       ('ars'),
       ('Germ'),
       ('andrei');

insert into reviews(body, commentator, game, mark)
    values ('aaaaa',1,1,5),
           ('nice',2,1,4),
           ('aaab',3,3,1),
           ('norm igra',4,4,5);
insert into client2game(id_client, game_id)
values (1,1),
       (1,2),
       (1,3),
       (2,2),
       (3,3),
       (4,2)

DROP MATERIALIZED VIEW games_mater;


       create
materialized view games_mater as
select games.name as "Gamename", games.id as "Game_id",developer as "GameDev", "genre",reviews.id as "rev_id",reviews.body as "Review", reviews.mark as "rev_mark", c.name as "Cient Name", c.id as "Client_id"
            from games
            left join reviews on "game" = games.id
            left join client2game  c2g on games.id = c2g.game_id
            left join client c on c.id = c2g.id_client;
select * from games_mater