from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
from psycopg2.extras import DictCursor
import re
 
app = Flask(__name__)
 
# Configure PostgreSQL database connection
app.config['POSTGRESQL_HOST'] = 'localhost'
app.config['PORT']=5433
app.config['POSTGRESQL_USER'] = 'postgres'  # Replace with your PostgreSQL username
app.config['POSTGRESQL_PASSWORD'] = 'root'  # Replace with your PostgreSQL password
app.config['POSTGRESQL_DB'] = 'postgres'
app.secret_key = 'your_secret_key'  # Replace with your secret key
 
def get_db_connection():
    conn = psycopg2.connect(
        host=app.config['POSTGRESQL_HOST'],
        port=app.config['PORT'],
        user=app.config['POSTGRESQL_USER'],
        password=app.config['POSTGRESQL_PASSWORD'],
        dbname=app.config['POSTGRESQL_DB']
    )
    return conn
 
@app.route('/')
def index():
    return render_template('index.html')
 
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        cursor.close()
        conn.close()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
 
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)', (username, password, email))
            conn.commit()
            msg = 'You have successfully registered!'
        cursor.close()
        conn.close()
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)
 
@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))
 
if __name__ == '__main__':
    app.run(debug=True,port=5007)
