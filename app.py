from pyexpat.errors import messages

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors


app = Flask(__name__)
app.secret_key = "meowmeowguliguli"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'forumapp'
app.config['MYSQL_PASSWORD'] = 'guliguli'
app.config['MYSQL_DB'] = 'forums'
mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM forum_users WHERE email = % s AND password = % s', (email, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['user_id']
            session['name'] = user['name']
            session['email'] = user['email']
            session['role'] = user['usergroup']
            message = 'logged in'
            return redirect(url_for('category'))
        else:
            message = 'Please enter correct email and password !'
    return render_template('login.html', message = message)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    session.pop('role', None)
    session.pop('name', None)
    return  redirect(url_for('login'))

@app.route('/category', methods = ['GET', 'POST'])
def category():
    if request.args.get('category_id'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT c.name, t.category_id, t.subject, t.topic_id, t.user_id, '
            'FROM forum_topics as t '
            'LEFT JOIN forum_posts as p ON t.topic_id = p.topic_id '
            'LEFT JOIN forum_category as c ON t.category_id = c.category_id '
            'WHERE t.category_id = %s '
            'GROUP BY t.topic_id ORDER BY t.topic_id DESC',
            (request.args.get('category_id'),)
        )
        topics = cursor.fetchall()

        cursor.execute(
            'SELECT category_id, name FROM forum_category WHERE category_id = %s',
            (request.args.get('category_id'),)
        )
        category = cursor.fetchone()

        return render_template("category.html", topics=topics, category=category, request=request)

    else:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT category.category_id, category.name, category.description, '
            'count(topic.category_id) AS total_topic '
            'FROM forum_category category '
            'LEFT JOIN forum_topics topic ON category.category_id = topic.category_id '
            'GROUP BY category.category_id ORDER BY category_id DESC'
        )
        categories = cursor.fetchall()
        return render_template("category.html", categories=categories, request=request)

@app.route('/compose', methods = ['GET', 'POST'])
def compose():
    if 'loggedin' in session:
        if request.args.get('category_id'):
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute('SELECT category_id, name FROM forum_category WHERE category_id = %s ', (request.args.get('category_id'),))
            category = cursor.fetchone()

            return render_template('compose.html', category = category)

        return redirect(url_for('login'))

@app.route("/save_topic", methods = ['GET', 'POST'])
def save_topic():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'categoryId' in request.form and 'topicName' in request.form and 'message' in request.form:

            categoryId = request.form['categoryId']
            topicName = request.form['topicName']
            message = request.form['message']

            cursor.execute('INSERT INTO forum_topics (`subject`, `category_id`, `user_id`) VALUES (%s, %s, %s)', (topicName, categoryId, message))
            mysql.connection.commit()

            lastInsertTopicId = cursor.lastrowid
            cursor.execute('INSERT INTO forum_posts (`message`, `topic_id`, `user_id`) VALUES (%s, %s, %s)', (message, lastInsertTopicId, session['userid']))
            mysql.connection.commit()

            return redirect(url_for('category', category_id=categoryId))

    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
