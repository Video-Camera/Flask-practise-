import sqlite3
from flask import Flask, request, jsonify, redirect, url_for, render_template
from flask_cors import CORS


def connect_to_db():
    connection = sqlite3.connect('mydb.db')
    return connection


def insert_user(user):
    inserted_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO user (Username, Password) VALUES (?, ?)", (user['Username'], user['Password']))
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
            user = {}
            user["UserId"] = i["UserId"]
            user["Username"] = i["Username"]
            user["Password"] = i["Password"]
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
        cur.execute("SELECT * FROM user WHERE UserId = ?", (user_id,))
        row = cur.fetchone()
        user['UserId'] = row['UserId']
        user['username'] = row['username']
        user['password'] = row['password']

    except:
        user = {}

    return user


def update_user(user):
    updated_user = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE user SET Username = ?, Password = ? WHERE UserId = ?",
                    (user['Username'], user['Password'], user['UserId']))
        conn.commit()
        updated_user = get_user_by_id(user['UserId'])
    except:
        connect_to_db().rollback()
        updated_user = {}
    finally:
        connect_to_db().close()
    return updated_user


def delete_user(user_id):
    user_id = int(user_id)
    message = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("DELETE from user WHERE UserId = ?", (user_id,))
        conn.commit()
        message['status'] = 'USER DELETE'
    except:
        connect_to_db().rollback()
        message['status'] = "Can't delete"
    finally:
        connect_to_db().close()
    return message


def get_products():
    products = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql_command = """SELECT * FROM product"""
        cur.execute(sql_command)
        rows = cur.fetchall()
        for x in rows:
            product = {}
            product['ProductId'] = x['ProductId']
            product['ProductName'] = x['ProductName']
            product['ProductPrice'] = x['ProductPrice']
            products.append(product)
    except:
        product = []
    finally:
        connect_to_db().close()
    return products


def get_product_by_id(product_id):
    product = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM product WHERE ProductId = ?", (product_id,))
        row = cur.fetchone()
        product['ProductId'] = row['ProductId']
        product['ProductName'] = row['ProductName']
        product['ProductPrice'] = row['ProductPrice']
    except:
        product = {}
    finally:
        connect_to_db().close()
    return product


def add_product(product):
    inserted_product = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("INSERT INTO product (ProductName, ProductPrice) VALUES (?, ?)",
                    (product["ProductName"], product["ProductPrice"]))
        conn.commit()
        inserted_product = get_product_by_id(cur.lastrowid)
    except:
        inserted_product = {}
    finally:
        connect_to_db().close()
    return inserted_product


def get_orders_by_id(user_id):
    user_orders = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""SELECT norder.OrderCustomerId, norder.OrderProductId, product.ProductName, product.ProductPrice, user.Username
                                    FROM norder
                                    INNER JOIN product ON norder.OrderProductId = product.ProductId
                                    INNER JOIN user on norder.OrderCustomerId = user.UserId
                                    WHERE norder.OrderCustomerId = ?""", (user_id,))
        list_of_orders = cur.fetchall()
        for x in list_of_orders:
            norder = {}
            norder["OrderCustomerId"] = x['OrderCustomerId']
            norder["OrderProductId"] = x['OrderProductId']
            norder["ProductName"] = x['ProductName']
            norder["ProductPrice"] = x['ProductPrice']
            norder["Username"] = x['Username']
            user_orders.append(norder)
    except:
        user_orders = []
    finally:
        connect_to_db().close()
    return user_orders


def show_carts():
    user_carts = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        curr = conn.cursor()
        curr.execute("""SELECT cart.Customer_id, cart.CartProductId, product.ProductName, product.ProductPrice, user.Username
                        FROM cart
                        INNER JOIN product ON cart.CartProductId = product.ProductId
                        INNER JOIN user ON cart.Customer_id = user.UserId""")
        list_of_carts = curr.fetchall()
        for x in list_of_carts:
            cart = {}
            cart['Customer_id'] = x['Customer_id']
            cart['CartProductId'] = x['CartProductId']
            cart['ProductName'] = x['ProductName']
            cart['ProductPrice'] = x['ProductPrice']
            cart['Username'] = x['Username']
            user_carts.append(cart)
    except:
        user_carts = []
    finally:
        connect_to_db().close()
    return user_carts


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": '*'}})


@app.route("/api/users", methods=["GET"])
def api_get_users():
    return jsonify(get_users())


@app.route('/api/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    return jsonify(get_user_by_id(user_id))


@app.route('/api/users/add', methods=['POST'])
def api_add_user():
    user_payload = request.get_json()
    persisted_user = insert_user(user_payload)
    return jsonify(persisted_user)


@app.route('/api/users/update', methods=['PUT'])
def api_update_user():
    user = request.get_json()
    return jsonify(update_user(user))


@app.route('/api/users/delete/<user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    return jsonify(delete_user(user_id))


@app.route("/api/products", methods=["GET"])
def api_get_products():
    return jsonify(get_products())


@app.route("/api/products/<product_id>", methods=["GET"])
def api_get_product(product_id):
    return jsonify(get_product_by_id(product_id))


@app.route("/api/products/add", methods=["POST"])
def api_add_product():
    product_payload = request.get_json()
    persisted_product = add_product(product_payload)
    return jsonify(persisted_product)


@app.route("/api/orders/<user_id>", methods=['GET'])
def api_get_orders_by_id(user_id):
    return jsonify(get_orders_by_id(user_id))


@app.route("/api/carts", methods=['GET'])
def api_get_carts():
    return jsonify(show_carts())


# Create User and add to sql database.
@app.route("/createuser", methods=["POST", "GET"])
def create_user():
    if request.method == "POST":
        user_name = request.form["Username"]
        user_password = request.form["Password"]
        try:
            conn = connect_to_db()
            curr = conn.cursor()
            curr.execute("""INSERT INTO user (Username, Password) VALUES (?, ?)""", (user_name, user_password))
            conn.commit()

        except:
            connect_to_db().rollback()
        finally:
            connect_to_db().close()
        return redirect(url_for("user", usr=user_name))
    else:
        return render_template('login.html')



@app.route("/<usr>")
def user(usr):
    return f"<h1> {usr}</h1>"
@app.route("/api/home")
def home():
    return render_template("index.html")



if __name__ == "__main__":
    app.debug = True
    app.run(debug=True)
    app.run()  # run app
