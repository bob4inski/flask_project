во Первых что мы делали
создаем контейнер редиса: 

    docker run --name redis_db2022 -p 26596:6379 -d redis --requirepass redis

потом   создаем папку для нашего проекта
заходим в эту папку через терминал и делаем вот такую грязь:

    apt install python3.9-venv
    python3.9 -m venv venv
    source venv/bin/activate

потом в файле requirements.txt устанавливаем нужныезависимости и в той же папке тыкаем:
    pip install -r requirements.txt

потом вот такую 
    export FLASK_APP=main.py
    export FLASK_ENV=development

и после чего пишем 
    flask run

yoyo apply --database postgresql://postgres:postgres@127.0.0.1:23891/lab ./migrations
     
yoyo apply --database postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@host.docker.internal:${POSTGRES_PORT}/${POSTGRES_DB} ./migrations
     
http://127.0.0.1:5000/games/currentrew?mark=3&commentator=4&body=%27%27

http://127.0.0.1:5000/games/idex?client_id=1&game_id=1&rev_id=2&