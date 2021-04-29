from flask import Flask, jsonify
import mysql.connector as mysql

service = Flask(__name__)

IS_ALIVE = 'yes'
DEBUG = True
FEEDS_PER_PAGE = 4

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

def get_total_likes(feed_id):
    likes = 0
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f'SELECT count(*) as likes FROM likes WHERE feed = {feed_id}')

    result = cursor.fetchone()

    if result:
        likes = result['likes']

    return likes


def generate_feed(record):
    return {
        '_id': record['feed_id'],
        'datetime': record['feed_date'],
        'author': {
            '_id': record['author_id'],
            'name': record['author_name'],
            'avatar': record['avatar']
        },
        'likes': record['likes'],
        'post': {
            'title': record['post_title'],
            'description': record['body'],
            'url': record['url'],
            'blobs': [
                {
                    'type': 'image',
                    'file': record['image1']
                },
                {
                    'type': 'image',
                    'file': record['image2']
                },
                {
                    'type': 'image',
                    'file': record['image3']
                }
            ]
        }
    }

@service.route('/feeds/<int:page>')
def get_feeds(page):
    feeds = []
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT feeds.id as feed_id, DATE_FORMAT(feeds.date, '%Y-%m-%d T') as feed_date, " + 
        "authors.id as author_id, authors.name as author_name, authors.avatar, " +
        "posts.title as post_title, posts.body, posts.url, posts.image1, IFNULL(posts.image2, '') as image2, IFNULL(posts.image3, '') as image3 " +
        "FROM feeds, posts, authors " +
        "WHERE posts.id = feeds.post " +
        "AND authors.id = posts.author " +
        "ORDER BY feed_date DESC " +
        "LIMIT " + str((page -1) * FEEDS_PER_PAGE) + ", " + str(FEEDS_PER_PAGE)
    )

    result = cursor.fetchall()

    for record in result:
        record['likes'] = get_total_likes(record['feed_id'])
        feeds.append(generate_feed(record))

    return jsonify(feeds)

@service.route('/feed/<int:feed_id>')
def get_feed(feed_id):
    feed = {}
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT feeds.id as feed_id, DATE_FORMAT(feeds.date, '%Y-%m-%d T') as feed_date, " + 
        "authors.id as author_id, authors.name as author_name, authors.avatar, " +
        "posts.title as post_title, posts.body, posts.url, posts.image1, IFNULL(posts.image2, '') as image2, IFNULL(posts.image3, '') as image3 " +
        "FROM feeds, posts, authors " +
        "WHERE posts.id = feeds.post " +
        "AND authors.id = posts.author " +
        "AND feeds.id = " + str(feed_id) + ";"
    )

    record = cursor.fetchone()

    if record:
        record['likes'] = get_total_likes(record['feed_id'])
        feed = generate_feed(record)

    return jsonify(feed)

@service.route('/feeds/search/<string:post_title>/<int:page>')
def get_feeds_by_post_title(post_title, page):
    feeds = []
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT feeds.id as feed_id, DATE_FORMAT(feeds.date, '%Y-%m-%d T') as feed_date, " + 
        "authors.id as author_id, authors.name as author_name, authors.avatar, " +
        "posts.title as post_title, posts.body, posts.url, posts.image1, IFNULL(posts.image2, '') as image2, IFNULL(posts.image3, '') as image3 " +
        "FROM feeds, posts, authors " +
        "WHERE posts.id = feeds.post " +
        "AND authors.id = posts.author " +
        "AND posts.title LIKE '%" + post_title + "%' " + 
        "ORDER BY feed_date DESC " +
        "LIMIT " + str((page -1) * FEEDS_PER_PAGE) + ", " + str(FEEDS_PER_PAGE)
    )

    result = cursor.fetchall()

    for record in result:
        record['likes'] = get_total_likes(record['feed_id'])
        feeds.append(generate_feed(record))

    return jsonify(feeds)

@service.route('/feeds/author/<int:author_id>/<int:page>')
def get_feeds_by_author(author_id, page):
    feeds = []
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT feeds.id as feed_id, DATE_FORMAT(feeds.date, '%Y-%m-%d T') as feed_date, " + 
        "authors.id as author_id, authors.name as author_name, authors.avatar, " +
        "posts.title as post_title, posts.body, posts.url, posts.image1, IFNULL(posts.image2, '') as image2, IFNULL(posts.image3, '') as image3 " +
        "FROM feeds, posts, authors " +
        "WHERE posts.id = feeds.post " +
        "AND authors.id = posts.author " +
        "AND authors.id = " + str(author_id) + " " + 
        "ORDER BY feed_date DESC " +
        "LIMIT " + str((page -1) * FEEDS_PER_PAGE) + ", " + str(FEEDS_PER_PAGE)
    )

    result = cursor.fetchall()

    for record in result:
        record['likes'] = get_total_likes(record['feed_id'])
        feeds.append(generate_feed(record))

    return jsonify(feeds)


if __name__ == '__main__':
    service.run(
        host='0.0.0.0',
        debug=DEBUG,
        port='5000'
    )
    