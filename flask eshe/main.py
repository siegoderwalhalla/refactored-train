import os
from flask import Flask, abort, request, redirect, render_template, jsonify, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
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

#@app.route('/')
#def index():
#    return render_template('index.html')

@app.route('/user/all')
@app.route('/user/<int:user_id>')
def get_user(user_id=None):
    connection, cursor = get_connection()

    if user_id is None:
        cursor.execut('''SELECT * FROM USERS''')
        users_data = cursor.fetchall()
        close_connection(connection, cursor)

        return [User(i[0], i[1], i[2]).__dict__ for i in users_data]

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

@app.route('/user/create/mob', methods=['POST'])
def create_user_mob():
    json = request.json
    login = json['login']
    password = json['pass']

    connection, cursor = get_connection()
    try:

        cursor.execute('''INSERT INTO USERS(login, password)
        VALUES (%s, %s);''', (login, password))

        connection.commit()

    except Exception:
        return abort(400, 'Login must be unique')
    finally:
        close_connection(connection, cursor)
    return jsonify(success='ok')

#'txt', 'docx', 'pdf'
UPLOAD_FOLDER = './files'
ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # проверить, есть ли в запросе post часть файла
        if 'file' not in request.files:
            #flash('No file part')
            return abort(400, 'No file')
        file = request.files['file']
        # Если пользователь не выбирает файл, браузер отправляет
        # пустой файл без имени файла.
        if file.filename == '':
            #flash('No selected file') return redirect(request.url)
            return abort(400, "no selected file")
        if file and allowed_file(file.filename):
            #filename = secure_filename(file.filename) в основном юзается на линуксе (по названию файла ищет секретное название файла и берет хэш от его названия)
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return render_template('files.html')

@app.route('/uploads/<name>')
def download_file(name):
    # name += '.png' - для красоты урла
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)

    #ALTER TABLE users
    #ADD COLUMN img_url VARCHAR(120) DEFAULT 'БАШУиеавч.png'

    #UPDATE users SET img_url = 'анимация 001-01.png' WHERE login LIKE 'root%'