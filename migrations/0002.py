from yoyo import step


steps = [
   step(
       """
        insert into games(name, developer, genre)
values ('Forza','ea games','racing'),
       ('wot','lartoshla','arcade'),
       ('maincampf','maicrosoft','aboba'),
       ('call of duty','idn','wars');

insert into client(name,age)
values ('robert',12),
       ('ars',15),
       ('Germ',26),
       ('andrei',17),
       ('arseniy',10),
       ('magic aboba',120),
       ('keril',20);

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
       (4,2),
       (4,4),
       (6,1),
       (7,4),
       (5,4),
       (6,2),
       (5,3);
       """
   )
]
