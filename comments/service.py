from flask import Flask, jsonify
import mysql.connector as mysql

service = Flask(__name__)

IS_ALIVE = 'yes'
DEBUG = True
COMMENTS_PER_PAGE = 8

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

def generate_comment(comment):
    return {
        '_id': comment['id'],
        'feed': comment['feed'],
        'user': {
            'account': comment['account'],
            'name': comment['name']
        },
        'datetime': comment['date'],
        'content': comment['comment']
    }

@service.route('/comments/<int:feed_id>/<int:page>')
def get_comments(feed_id, page):
    comments = []
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, feed, comment, name, account, DATE_FORMAT(date, '%Y-%m-%d T') as date " + 
        "FROM comments " +
        "WHERE feed = " + str(feed_id) + " " + 
        "ORDER BY date DESC " + 
        "LIMIT " + str((page-1) * COMMENTS_PER_PAGE) + ", " + str(COMMENTS_PER_PAGE)
    )

    result = cursor.fetchall()

    for record in result:
        comments.append(generate_comment(record))

    return jsonify(comments)

@service.route('/comments/add/<int:feed_id>/<string:name>/<string:email>/<string:text>')
def add(feed_id, name, email, text):
    result = jsonify(situation='ok', error='')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "INSERT INTO comments(comment, feed, name, account, date) " + 
            f"VALUES ('{text}', {feed_id}, '{name}', '{email}', NOW())"
        )
        connection.commit()
    except:
        connection.rollback()
        result = jsonify(situation='error', error='Erro adicionando comentário')

    return result

@service.route('/comments/remove/<int:comment_id>')
def remove(comment_id):
    result = jsonify(situation='ok', error='')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"DELETE FROM comments WHERE id = {comment_id}.;")
        connection.commit()
    except:
        connection.rollback()
        result = jsonify(situation='error', error='Erro removendo comentário')

    return result

if __name__ == '__main__':
    service.run(
        host='0.0.0.0',
        debug=DEBUG,
        port='5001'
    )