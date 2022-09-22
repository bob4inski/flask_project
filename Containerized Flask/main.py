from flask import Flask, jsonify, request
from psycopg2.extras import RealDictCursor
import psycopg2
from redis import Redis
import json
import os

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


@app.route('/holders')
def get_holders():
    try:
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        redis_key = f'holders:offset={offset},limit={limit}'
        with get_redis_connection() as redis_conn:
            redis_holders = redis_conn.get(redis_key)

        if redis_holders is None:
            query = """
            select *
            from holder
            order by phone
            offset %s
            limit %s
            """

            with get_pg_connection() as pg_conn, pg_conn.cursor() as cur:
                cur.execute(query, (offset, limit))
                rows = cur.fetchall()

            redis_holders = json.dumps(rows, ensure_ascii=False, default=str, indent=2)

            with get_redis_connection() as redis_conn:
                redis_conn.set(redis_key, redis_holders, ex=30)

        return redis_holders, 200, {'content-type': 'text/json'}
    except Exception as ex:
        return {'message': repr(ex)}, 400


@app.route('/holders/create', methods=['POST'])
def create_holder():
    try:
        body = request.json
        name = body['name']
        phone = body['phone']

        query = """
        insert into holder (phone, name)
        values (%s, %s)
        returning phone, name
        """

        with get_pg_connection() as pg_conn, pg_conn.cursor() as cur:
            cur.execute(query, (phone, name))
            rows = cur.fetchall()

        return {'message': f'Holder {rows[0]["name"]} with phone = {rows[0]["phone"]} created.'}
    except Exception as ex:
        return {'message': repr(ex)}, 400


@app.route('/holders/update', methods=['POST'])
def update_holder():
    try:
        body = request.json
        name = body['name']
        phone = body['phone']

        query = """
        update holder
        set name = %s
        where phone = %s
        returning phone
        """

        with get_pg_connection() as pg_conn, pg_conn.cursor() as cur:
            cur.execute(query, (name, phone))
            affected_rows = cur.fetchall()

        if len(affected_rows):
            return {'message': f'Holder with phone = {phone} updated.'}
        else:
            return {'message': f'Holder with phone = {phone} not found.'}, 404
    except Exception as ex:
        return {'message': repr(ex)}, 400


@app.route('/holders/delete', methods=['DELETE'])
def delete_holder():
    try:
        body = request.json
        phone = body['phone']

        query = """
        delete from holder
        where phone = %s
        returning phone
        """

        with get_pg_connection() as pg_conn, pg_conn.cursor() as cur:
            cur.execute(query, (phone,))
            affected_rows = cur.fetchall()

        if len(affected_rows):
            return {'message': f'Holder with phone = {phone} deleted.'}
        else:
            return {'message': f'Holder with phone = {phone} not found.'}, 404
    except Exception as ex:
        return {'message': repr(ex)}, 400
