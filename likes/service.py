from flask import Flask, jsonify
import mysql.connector as mysql

service = Flask(__name__)

IS_ALIVE = 'yes'
DEBUG = True

MYSQL_SERVER = 'devsblog_database'
MYSQL_USER = 'root'
MYSQL_PASS = 'admin'
MYSQL_DATABASE = 'devsblog'

def get_db_connection():
    return mysql.connect(
        host=MYSQL_SERVER,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DATABASE
    )

@service.route('/liked/<string:email>/<int:feed_id>')
def liked(email, feed_id):
    likes = 0
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT count(*) as num_likes FROM likes WHERE email = '{email}' AND feed = {str(feed_id)}")
    record = cursor.fetchone()

    if record:
        likes = record['num_likes']

    return jsonify(likes = likes)

@service.route('/like/<string:email>/<int:feed_id>')
def like(email, feed_id):
    result = jsonify(situation='ok', error='')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"INSERT INTO likes(feed, email) VALUES ({feed_id}, '{email}')")
        connection.commit()
    except:
        connection.rollback()
        result = jsonify(situation='error', error='Erro adicionando like')

    return result

@service.route('/dislike/<string:email>/<int:feed_id>')
def dislike(email, feed_id):
    result = jsonify(situation='ok', error='')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"DELETE FROM likes WHERE feed = {feed_id} AND email = '{email}'")
        connection.commit()
    except:
        connection.rollback()
        result = jsonify(situation='error', error='Erro removendo like')

    return result

if __name__ == '__main__':
    service.run(
        host='0.0.0.0',
        debug=DEBUG,
        port='5002'
    )
    