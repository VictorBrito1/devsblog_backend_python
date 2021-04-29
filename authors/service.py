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

def generate_author(author):
    return {
        '_id': author['id'],
        'name': author['name'],
        'avatar': author['avatar']
    }

@service.route('/authors')
def get_authors():
    authors = []
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, name, avatar FROM authors")
    result = cursor.fetchall()

    for record in result:
        authors.append(generate_author(record))
    
    return jsonify(authors)

if __name__ == '__main__':
    service.run(
        host='0.0.0.0',
        debug=DEBUG,
        port='5003'
    )
    