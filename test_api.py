import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

def connect_to_db():
    connection = sqlite3.connect('mydb.db')
    return connection

def insert_user(user):
    inserted_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO user (username, password) VALUES (?, ?)", (user['username'], user['password']))
        conn.commit()
        inserted_user = get_user_by_id(cur.lastrowid)
    except:
        connect_to_db().rollback()

    finally:
        connect_to_db().close()

    return inserted_user


def get_users():
    users = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""SELECT * FROM user""")
        rows = cur.fetchall()
        for i in rows:
            user = {'UserId': i['UserId'], 'Username': i['Username'], 'Password': i['Password']}
            users.append(user)
    except:
        user = []
    return users

def get_user_by_id(user_id):
    user = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM user WHERE UserId = ?", (user_id, ))
        row = cur.fetchone()
        user['UserId'] = row['UserId']
        user['username'] = row['username']
        user['password'] = row['password']

    except:
        user = {}

    return user

def update_user():
    


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": '*'}})

@app.route("/api/users", methods=["GET"])
def api_get_users():
    return jsonify(get_users())

@app.route('/api/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    return jsonify(get_user_by_id(user_id))

@app.route('/api/users/add',  methods = ['POST'])
def api_add_user():
    user_payload = request.get_json()
    persisted_user = insert_user(user_payload)
    return jsonify(persisted_user)

if __name__ == "__main__":
    app.debug = True
    app.run(debug=True)
    app.run() #run app
