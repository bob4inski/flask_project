
from http import client
from flask import Flask, jsonify, request
import psycopg2
from redis import Redis
import json
import os

from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


def get_pg_connection():
    pg_conn = psycopg2.connect(host=os.getenv('POSTGRES_HOST') or '127.0.0.1', port=os.getenv('POSTGRES_PORT'),
                               database=os.getenv('POSTGRES_DB'), user=os.getenv('POSTGRES_USER'),
                               password=os.getenv('POSTGRES_PASSWORD'), cursor_factory=RealDictCursor)
    pg_conn.autocommit = True
    return pg_conn


def get_redis_connection():
    return Redis(host=os.getenv('REDIS_HOST') or '127.0.0.1', port=os.getenv('REDIS_PORT'),
                 password=os.getenv('REDIS_PASSWORD'), decode_responses=True)


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
            review = reviews_dict[rev_id]
        elif rev_id is not None:
            review = Reviews(rev_id,rev_body,rev_mark)
            reviews_dict[rev_id] = review
        if rev_id is not None:
            if review not in game.reviews : game.reviews.append(review)
        if client_id is not None:
            if client not in game.clients : game.clients.append(client)
    return list(games_dict.values())  


    


@app.route('/games')
def get_games():
    try:
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        with get_redis_connection() as redis_conn:
            redis_key = f'games:offset={offset},limit={limit}'
            redis_games = redis_conn.get(redis_key)

        if redis_games is None:
            query = """
            select games.name as "Gamename", developer as "GameDev", "genre",reviews.id as "rev_id",reviews.body as "Review", reviews.mark as "rev_mark", c.name as "Cient Name", c.id as "Client_id"
            from games
            left join reviews on "game" = games.id
            left join client2game  c2g on games.id = c2g.game_id
            left join client c on c.id = c2g.id_client;
            """
            with get_pg_connection() as pg_conn, pg_conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

            games = deserl(rows)
            redis_games = json.dumps(games,default=vars,ensure_ascii=False, indent = 2)
            with get_redis_connection() as redis_conn:
                redis_conn.set(redis_key, redis_games, ex=30)

        
        return redis_games, 200, {'content-type': 'text/json'}
    except Exception as ex:
        return {'message': repr(ex)}, 400



@app.route('/games/create', methods=['POST'])
def create_game():
    try:
        body = request.json
        name = body['name']
        developer = body['developer']
        genre = body['genre']

        query = f"""
        insert into games (name, developer, genre)
        values (%s, %s, %s)
        returning name, developer, genre
        """
        with get_pg_connection() as pg_conn, pg_conn.cursor() as cur:
                cur.execute(query, (name, developer, genre))
                result = cur.fetchall()

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


# query=f"""
# with max_age as (select max(age) as age from client),
#      histogram as (select width_bucket(age, 0, (select age from max_age), 9) as bucket,
#                           count(*)                                                 as frequency
#                    from client
#                    group by bucket)
# select bucket,
#        frequency,
#        (bucket - 1) * (select age / 10 from max_age) as range_from,
#        bucket * (select age / 10 from max_age)       as range_to
# from histogram
# order by bucket;
# """

@app.route('/clients')
def get_a():
    try:
        cur = pg_conn.cursor()
        query=f"""
            with max_age as (select max(age) as age from client),
                histogram as (select width_bucket(age, 0, (select age from max_age), 9) as bucket,
                                    count(*)                                                 as frequency
                            from client
                            group by bucket)
            select bucket,
                frequency,
                (bucket - 1) * (select age / 10 from max_age) as range_from,
                bucket * (select age / 10 from max_age)       as range_to
            from histogram
            order by bucket;
            """
        cur.execute(query)
        graph = cur.fetchall()
        cur.close()
        
        redis_graph = json.dumps(graph,default=vars,ensure_ascii=False, indent = 2)
        return redis_graph, 200, {'content-type': 'text/json'}

    
    except Exception as ex:
        return {'message': repr(ex)}, 400
    pass


# @app.route('/games/currentrew')
# def get_currentreview():
#     try:
#         offset = request.args.get('offset')
#         limit = request.args.get('limit')
#         with get_redis_connection() as redis_conn:
#             redis_key = f'games:offset={offset},limit={limit}'
#             redis_games = redis_conn.get(redis_key)

#         if redis_games is None:
#             query = """
#             select * from reviews
#             where mark > 3 and commentator = 1 and body != '';
#             """
#             with get_pg_connection() as pg_conn, pg_conn.cursor() as cur:
#                 cur.execute(query)
#                 rew = cur.fetchall()

#             # games = deserl(rows)
#             redis_games = json.dumps(games,default=vars,ensure_ascii=False, indent = 2)
#             with get_redis_connection() as redis_conn:
#                 redis_conn.set(redis_key, redis_games, ex=30)

        
#         return redis_games, 200, {'content-type': 'text/json'}
#     except Exception as ex:
#         return {'message': repr(ex)}, 400

@app.route('/games/currentrew')
def get_currentreview():
    try:
        mark = request.args.get('mark')
        commentator = request.args.get('commentator')
        body = request.args.get('body')
        # with get_redis_connection() as redis_conn:
        #     redis_key = f'reviews:offset={offset},limit={limit}'
        #     redis_reviews = redis_conn.get(redis_key)


        # if redis_reviews is None:
        query = """
        select * from reviews
        where mark > %s and commentator = %s  and body != %s ;
        """
        with get_pg_connection() as pg_conn, pg_conn.cursor() as cur:
            cur.execute(query, (mark, commentator, body  ))
            reviews = cur.fetchall()

        if len(reviews):
            return jsonify(reviews)
        else:
            return {}, 404
    except Exception as ex:
        return {'message': repr(ex)}, 400



@app.route('/gamesmater')
def get_gamesmatter():
    try:
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        with get_redis_connection() as redis_conn:
            redis_key = f'games:offset={offset},limit={limit}'
            redis_games = redis_conn.get(redis_key)

        if redis_games is None:
            query = """
            select * from games_mater
            """
            with get_pg_connection() as pg_conn, pg_conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

            games = deserl(rows)
            redis_games = json.dumps(games,default=vars,ensure_ascii=False, indent = 2)
            with get_redis_connection() as redis_conn:
                redis_conn.set(redis_key, redis_games, ex=30)

        
        return redis_games, 200, {'content-type': 'text/json'}
    except Exception as ex:
        return {'message': repr(ex)}, 400

# ("Client_id", "Game_id", "rev_id")
@app.route('/games/idex')
def get_indexes():
    try:
        client_id = request.args.get('client_id')
        game_id = request.args.get('game_id')
        rev_id = request.args.get('rev_id')
        query = """
        select * from games_mater
        where "Client_id" = %s and "Game_id" = %s  and "rev_id" != %s ;
        """
        with get_pg_connection() as pg_conn, pg_conn.cursor() as cur:
            cur.execute(query, (client_id, game_id, rev_id  ))
            reviews = cur.fetchall()

        if len(reviews):
            return jsonify(reviews)
        else:
            return {}, 404
    except Exception as ex:
        return {'message': repr(ex)}, 400