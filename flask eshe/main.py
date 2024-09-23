from flask import Flask, abort, request, redirect, render_template, jsonify, url_for
from user import User
import psycopg2

app = Flask(__name__)
def get_connection():
    connection = psycopg2.connect(database='database', user='admini',
                                  password='root', host='localhost', port='5432')

    cursor = connection.cursor()

    return connection, cursor

def close_connection(conn, cur):
    conn.close()
    cur.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/all')
@app.route('/user/<int:user_id>')
def get_user(user_id=None):
    connection, cursor = get_connection()

    if user_id is None:
        cursor.execut('''SELECT * FROM USERS''')
        users_data = cursor.fetchall()
        close_connection(connection, cursor)

        return [User(i[0], i[1]).__dict__ for i in users_data]

    cursor.execute('''SELECT * FROM USERS WHERE user_order=%s''', [user_id])

    user_data = cursor.fetchall()

    close_connection(connection, cursor)

    if user_data.__len__() == 0:
        return abort(404, f"User with id {user_id} not found")

    return User(user_data[0][0], user_data[0][1]).__dict__

@app.route('/user/create', methods=['POST'])
def create_user():
    login = request.form['login']
    password = request.form['password']

    connection, cursor = get_connection()

    cursor.execute('''INSERT INTO USERS(login, password) 
    VALUES (%s, %s);''', (login, password))

    connection.commit()

    close_connection(connection, cursor)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()