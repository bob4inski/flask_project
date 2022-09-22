from yoyo import step


steps = [
   step(
       """
        insert into holder (name, phone)
        values ('Альберт Андреевич', '0001'),
               ('Иван Вячеславович', '0002'),
               ('Вячеслав Александрович', '0003'),
               ('Алексей Андреевич', '0004');
       """
   )
]