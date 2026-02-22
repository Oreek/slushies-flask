from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import hashlib

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
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = hashlib.md5((request.form['password']).encode('ISO-8859-1')).hexdigest()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM forum_users WHERE email = % s AND password = %s', (email, password,))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['user_id']
            session['name'] = user['name']
            session['email'] = user['email']
            session['role'] = user['usergroup']
            mesage = 'Logged in successfully !'
            return redirect(url_for('category'))
        else:
            mesage = 'Please enter correct email and password !'
    return render_template('login.html', mesage = mesage)

@app.route('/register', methods=['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'password' in request.form:
        name = request.form['name']
        email = request.form['email']
        password = hashlib.md5((request.form['password']).encode('ISO-8859-1')).hexdigest()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM forum_users WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            mesage = 'Account already exists!'
        elif not name or not email or not password:
            mesage = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO forum_users (name, email, password, usergroup) VALUES (%s, %s, %s, %s)', (name, email, password, 'member'))
            mysql.connection.commit()
            mesage = 'You have successfully registered! Please login.'
            return redirect(url_for('login'))

    return render_template('register.html', mesage=mesage)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    session.pop('name', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/category', methods = ['GET', 'POST'])
def category():
    if request.args.get('category_id'):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT c.name, t.category_id, t.subject, t.topic_id, t.user_id, '
            'count(p.post_id) AS total_post '
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

            cursor.execute('INSERT INTO forum_topics (`subject`, `category_id`, `user_id`) VALUES (%s, %s, %s)', (topicName, categoryId, session['userid']))
            mysql.connection.commit()

            lastInsertTopicId = cursor.lastrowid
            cursor.execute('INSERT INTO forum_posts (`message`, `topic_id`, `user_id`) VALUES (%s, %s, %s)', (message, lastInsertTopicId, session['userid']))
            mysql.connection.commit()

            return redirect(url_for('category', category_id=categoryId))

    return redirect(url_for('login'))

@app.route('/post', methods = ['GET', 'POST'])
def post():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.args.get('topic_id'):

        cursor.execute('SELECT topic_id, subject, category_id FROM forum_topics WHERE topic_id = %s ', (request.args.get('topic_id'),))
        topic = cursor.fetchone()

        cursor.execute('SELECT p.post_id, p.message, p.topic_id, p.user_id, p.created, u.name AS username FROM forum_posts p LEFT JOIN forum_users u ON u.user_id = p.user_id WHERE p.topic_id = %s ', (request.args.get('topic_id'),))

        posts = cursor.fetchall()

        return render_template('post.html', topic = topic, posts = posts)

@app.route('/save_post', methods = ['GET', 'POST'])
def save_post():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'topic_id' in request.form and 'message' in request.form:
            topicId = request.form['topic_id']
            message = request.form['message']

            cursor.execute('INSERT INTO forum_posts (`message`, `topic_id`, `user_id`) VALUES (%s, %s, %s)', (message, topicId, session['userid']))
            mysql.connection.commit()

            return redirect(url_for('post', topic_id=topicId))

    return redirect(url_for('login'))

@app.route('/edit_post', methods = ['GET', 'POST'])
def edit_post():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.args.get('post_id'):
            postId = request.args.get('post_id')

            cursor.execute('SELECT post_id, message, topic_id FROM forum_posts WHERE post_id = %s ', (postId,))
            post = cursor.fetchone()
            cursor.execute('SELECT topic_id, subject, category_id FROM forum_topics WHERE topic_id = %s ', (post['topic_id'],))
            topic = cursor.fetchone()

            return render_template('edit_post.html', post = post, topic = topic)

    return redirect(url_for('login'))

@app.route('/save_edit', methods = ['GET', 'POST'])
def save_edit():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if request.method == 'POST' and 'postId' in request.form and 'message' in request.form:
            postId = request.form['postId']
            message = request.form['message']
            topicId = request.form['topicId']

            cursor.execute('UPDATE forum_posts SET message = %s WHERE post_id = %s', (message, postId ))
            mysql.connection.commit()

            return redirect(url_for('post', topic_id = topicId))

    return  redirect(url_for('login'))


@app.route('/delete_post', methods = ['GET'])
def delete_post():
    if 'loggedin' in session:
        postId = request.args.get('post_id')
        if postId:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute('SELECT post_id, topic_id, user_id FROM forum_posts WHERE post_id = %s', (postId,))
            post = cursor.fetchone()

            if post and (post['user_id'] == session['userid'] or session.get('role') == 'admin'):
                cursor.execute('DELETE FROM forum_posts WHERE post_id = %s', (postId,))
                mysql.connection.commit()
                return redirect(url_for('post', topic_id=post['topic_id']))

    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
