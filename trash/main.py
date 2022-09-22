
from http import client
from flask import Flask, jsonify, request
import psycopg2
from redis import Redis
import json

from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

pg_conn = psycopg2.connect(database='lab', user='postgres', password='postgres', host='localhost', port=23891,
                        cursor_factory=RealDictCursor)
pg_conn.autocommit = True

redis_conn = Redis(port=26596, password='redis', decode_responses=True)

class Client:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class Games:
    # def __init__(self, id: int, name: str,developer: str, genre: str):
    def __init__(self, name: str,developer: str, genre: str):
        # self.id = id
        self.name = name
        self.developer = developer
        self.genre = genre
        self.reviews: List[Reviews] = []
        self.clients: List[Client] = []
        
class Reviews:
    def __init__(self, id: int, body: str,mark:int):
        self.id = id
        self.body = body
        self.mark = mark

def deserl(rows):
    clients_dict = {}
    reviews_dict = {}
    games_dict = {}
    for row in rows:
        game_name = row['Gamename']
        game_dev = row['GameDev']
        game_genre = row['genre']

        game = None
        if game_name in games_dict:
            game = games_dict[game_name]
        else:
            game = Games(game_name,game_dev,game_genre)
            games_dict[game_name] = game
        

        client_name = row['Cient Name']
        client_id = row['Client_id']

        
        client = None
        if client_id in clients_dict:
            client = clients_dict[client_id]
        elif client_id is not None:
            client = Client(client_id,client_name)
            clients_dict[client_id] = client
        
        rev_id = row["rev_id"]
        rev_body = row["Review"]
        rev_mark = row["rev_mark"]
        review = None
        if rev_id in reviews_dict:
            review = review[rev_id]
        elif rev_id is not None:
            review = Reviews(rev_id,rev_body,rev_mark)
            reviews_dict[rev_id] = review
        if rev_id is not None:
            if review not in game.reviews : game.reviews.append(review)
        if client_id is not None:
            if client not in game.clients : game.clients.append(client)
    return list(games_dict.values())  


    


@app.route('/games')
def get_reviews():
    try:
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        redis_key = f'games:offset={offset},limit={limit}'
        redis_games = redis_conn.get(redis_key)

        if redis_games is None:
            cur = pg_conn.cursor()
            query = """
            select games.name as "Gamename", developer as "GameDev", "genre",reviews.id as "rev_id",reviews.body as "Review", reviews.mark as "rev_mark", c.name as "Cient Name", c.id as "Client_id"
            from games
            left join reviews on "game" = games.id
            left join client2game  c2g on games.id = c2g.game_id
            left join client c on c.id = c2g.id_client;
            """
            cur.execute(query, (offset, limit))
            games = cur.fetchall()
            cur.close()
            games = deserl(games)
            redis_conn.set(redis_key, json.dumps(games,default=vars,ensure_ascii=False), ex=30)
        else:
            games = json.loads(redis_games)

        if len(games):
            return jsonify(games)
        else:
            return {}, 404
    except Exception as ex:
        return {'message': repr(ex)}, 400



@app.route('/games/create', methods=['POST'])
def create_holder():
    try:
        body = request.json
        name = body['name']
        developer = body['developer']
        genre = body['genre']


        cur = pg_conn.cursor()
        query = f"""
        insert into games (name, developer, genre)
        values (%s, %s, %s)
        returning name, developer, genre
        """

        cur.execute(query, (name, developer, genre))
        result = cur.fetchall()
        cur.close()
        return {'message': f'Game {result[0]["name"]} that created by  = {result[0]["developer"]} was created.'}
    except Exception as ex:
        return {'message': repr(ex)}, 400


@app.route('/games/update', methods=['POST'])
def update_games():
    try:
        body = request.json
        name = body['name']
        developer = body['developer']

        cur = pg_conn.cursor()
        query = f"""
        update games
        set developer = %s
        where name = %s
        returning name, developer
        """

        cur.execute(query, (developer, name ))
        affected_rows = cur.fetchall()
        cur.close()

        if len(affected_rows):
            return {'message': f'Game = {name} updated.'}
        else:
            return {'message': f'Game = {name} not found.\n {affected_rows}'}, 404
    except Exception as ex:
        return {'message': repr(ex)}, 400


@app.route('/games/delete', methods=['DELETE'])
def delete_games():
    try:
        body = request.json
        name = body['name']

        cur = pg_conn.cursor()
        query = f"""
        delete from games
        where name = %s
        returning name
        """

        cur.execute(query, (name,))
        affected_rows = cur.fetchall()
        cur.close()

        if len(affected_rows):
            return {'message': f'game  {name} deleted.'}
        else:
            return {'message': f'game {name} not found.'}, 404
    except Exception as ex:
        return {'message': repr(ex)}, 400
