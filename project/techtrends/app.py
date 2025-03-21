import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

import logging
import sys
import datetime

# init all variables
db_connection_count = 0
post_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    
    global db_connection_count
    db_connection_count += 1
   
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    
    global post_count
    post_count += 1

    if post is not None:
        logging.info(str(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")) + ", article \"" + post['title'] + "\" is retrieved!")   
        
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logging.info(str(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")) + ', error: article ' + str(post_id) + ' is not known!')
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info(str(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")) + ", The \"About Us\" page is retrieved!")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            logging.info(str(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")) + ", new arcticle: \"" + title + "\" with content: \"" + content + "\" is created!")

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    return response

@app.route('/metrics')
def metrics():
    global db_connection_count
    global post_count
    response = app.response_class(
            response=json.dumps({"db_connection_count":db_connection_count,"post_count":post_count}),
            status=200,
            mimetype='application/json'
    )
    return response

# start the application on port 3111
if __name__ == "__main__":
    # create handler for stdout and stderror and add them to root logger 
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stdout_handler.setLevel(logging.DEBUG)
    stderr_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    stdout_handler.setFormatter(formatter)
    stderr_handler.setFormatter(formatter)
    handlers = [stderr_handler, stdout_handler]    
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s', handlers=handlers)
    app.run(host='0.0.0.0', port='3111')
