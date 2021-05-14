import mysql.connector
from mysql.connector import Error
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import flask_praetorian

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from flask import Flask, jsonify, request, send_from_directory, render_template, redirect, url_for, session
from flask_cors import CORS
import uuid
import cloudinary
import cloudinary.uploader
from decimal import Decimal
import os
from dotenv import load_dotenv, find_dotenv


app = Flask(__name__)
CORS(app)
load_dotenv(find_dotenv())

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)


def create_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST_NAME"),
            user=os.environ.get("MYSQL_USER"),
            passwd=os.environ.get("MYSQL_PASSWORD"),
            database=os.environ.get("MYSQL_DATABASE")
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

cloudinary.config(
  cloud_name = os.environ.get("CLOUDINARY_NAME"),  
  api_key = os.environ.get("CLOUDINARY_API_KEY"),  
  api_secret = os.environ.get("CLOUDINARY_API_SECRET")  
)

@app.route('/inventorys/<acc_num>', methods=['GET'])
def get_inventory(acc_num):
    print(acc_num)
    # acc_num= int(acc_num)
    try:
        connection = create_db_connection()
        print(connection)
        cur = connection.cursor()
        cur.execute("""SELECT * FROM `%s`""" % (acc_num))
        row_headers=[x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data=[]
        for result in rv:
            json_data.append(dict(zip(row_headers,result)))
        return jsonify(json_data)
    except Error as err:
        print(f"Error: '{err}'")
    finally:
        cur.close() 
        connection.close()

@app.route('/inventorys/<baseball_card_id>+<front_public_id>+<back_public_id>', methods=['DELETE'])
def delete_inventory_item(baseball_card_id, front_public_id, back_public_id):
    connection = create_db_connection()
    cur = connection.cursor()

    try:
        if front_public_id != 0:
            cloudinary.uploader.destroy(front_public_id)
        if back_public_id != 0:
            cloudinary.uploader.destroy(back_public_id)
        cur.execute("""DELETE FROM baseball_card WHERE baseball_card_id = %(baseball_card_id)s""", { 'baseball_card_id': baseball_card_id })
        connection.commit()
        response = jsonify('Employee deleted successfully!')
        response.status_code = 200
        return response
    except Error as err:
        print(f"Error: '{err}'")
    finally:
        cur.close() 
        connection.close()

@app.route('/inventorys/<baseball_card_id>', methods=['GET'])
def get_inventory_item(baseball_card_id):
    try:
        connection = create_db_connection()
        cur = connection.cursor()
        ok_happy = cur.execute("""SELECT * FROM baseball_card WHERE baseball_card_id = %s""", (baseball_card_id))
        row_headers=[x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data=[]
        for result in rv:
            json_data.append(dict(zip(row_headers,result)))
        return jsonify(json_data[0])
    except Error as err:
        print(f"Error: '{err}'")
    finally:
        cur.close() 
        connection.close()
    
@app.route('/inventorys', methods=['POST'])
def post_inventory_item():
    try:
        connection = create_db_connection()
        cur = connection.cursor()
        values = request.get_json()
        print(values)
        baseball_card_id = str(uuid.uuid4())
        brand = values['brand']
        buy_date = values['buy_date']
        buy_price = values['buy_price']
        card_condition = values['card_condition']
        card_number = values['card_number']
        description = values['description']
        first_name = values['first_name']
        last_name = values['last_name']
        profit_loss = values['profit_loss']
        sell_date = values['sell_date']
        sell_price = values['sell_price']
        year = values['year']
        card_image_front = values['card_image_front']
        card_image_back = values['card_image_back']
        account_number = values['account_number']
        account_token = values['account_token']


        if len(card_image_front) > 0:
            uploadedResponse = cloudinary.uploader.upload(card_image_front)
            image_front_url = uploadedResponse['url']
            front_public_id = uploadedResponse['public_id']
        else:
            image_front_url = ""
            front_public_id = ""

        if len(card_image_back) > 0:      
            uploadedResponse2 = cloudinary.uploader.upload(card_image_back)
            image_back_url = uploadedResponse2['url']
            back_public_id = uploadedResponse2['public_id']
        else:
            image_back_url = ""
            back_public_id = ""

        sqlQuery = """INSERT INTO `%s` (baseball_card_id, brand, buy_date, buy_price, card_condition, card_number,
        description, first_name, last_name, profit_loss, sell_date, sell_price, year, card_image_front, card_image_back, front_public_id, back_public_id) 
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        bind_data = (account_number, baseball_card_id, brand, buy_date, buy_price, card_condition, card_number, description, first_name, last_name, profit_loss, sell_date, sell_price, year, image_front_url, image_back_url, front_public_id, back_public_id)

        cur.execute(sqlQuery, bind_data)
        connection.commit()
        response = jsonify('Inventory Item Added Successfully!')
        response.status_code = 200
        return response
    except Error as err:
        print(f"Error: '{err}'")
    finally:
        cur.close() 
        connection.close()

@app.route('/inventorys/<baseball_card_id>', methods=['PUT'])
def update_inventory_item(baseball_card_id):
    try:
        values = request.get_json()
        connection = create_db_connection()
        cur = connection.cursor()
   
        brand = values['brand']
        buy_date = values['buy_date']
        buy_price = Decimal(values['buy_price'])
        card_condition = values['card_condition']
        card_number = values['card_number']
        description = values['description']
        first_name = values['first_name']
        last_name = values['last_name']
        sell_date = values['sell_date']
        sell_price = Decimal(values['sell_price']) if values['sell_price'] != "" else ""
        year = values['year']
        profit_loss = (sell_price - buy_price) if values['sell_price'] != "" and values['buy_price'] != "" else ""
        card_image_front = values['card_image_front']
        card_image_back = values['card_image_back']
        front_public_id = values['front_public_id']
        back_public_id = values['back_public_id']

        if card_image_front == "":
            print("there must not be a front image here")
            image_front_url = ""
        elif len(card_image_front) > 100:
            if front_public_id != "":
                cloudinary.uploader.destroy(front_public_id)

            uploadedResponse = cloudinary.uploader.upload(card_image_front)
            image_front_url = uploadedResponse['url']
            front_public_id = uploadedResponse['public_id']
            print("this must be a different front image")    
        else:
            image_front_url = card_image_front
            print("This must be the same image")
        
        if card_image_back == "":
            print("there must not be a back image here")
            image_back_url = ""
        elif len(card_image_back) > 100:
            if back_public_id != "":
                cloudinary.uploader.destroy(back_public_id)

            uploadedResponse2 = cloudinary.uploader.upload(card_image_back)
            image_back_url = uploadedResponse2['url']
            back_public_id = uploadedResponse2['public_id']
            print("this must be a different back image")   
        else:
            image_back_url = card_image_back
            print("This must be the same image")

        sqlQuery = """UPDATE baseball_card SET brand=%s, buy_date=%s, buy_price=%s, card_condition=%s, card_number=%s,
        description=%s, first_name=%s, last_name=%s, profit_loss=%s, sell_date=%s, sell_price=%s, year=%s, card_image_front=%s, card_image_back=%s, front_public_id=%s, back_public_id=%s WHERE baseball_card_id=%s"""
        bind_data = (brand, buy_date, buy_price, card_condition, card_number, description, first_name, last_name, profit_loss, sell_date, sell_price, year, image_front_url, image_back_url, front_public_id, back_public_id, baseball_card_id)

        cur.execute(sqlQuery, bind_data)
        connection.commit()
        response = jsonify('Inventory Item updated successfully!')
        response.status_code = 200
        return response
    except Error as err:
        print(f"Error: '{err}'")
    finally:
        cur.close() 
        connection.close()

# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username != "test" or password != "test":
        return jsonify({"msg": "Bad username or password"}), 401

    if username and password:
        try:
            connection = create_db_connection()
            cur = connection.cursor()
            cur.execute("""SELECT * FROM accounts WHERE username = %(username)s""", {'username': username})
            access_token = create_access_token(identity=username)
            account_data_from_db = cur.fetchone()
            return_obj = {
                "account_number": account_data_from_db[0],
                "username": account_data_from_db[1],
                "token": access_token
            }
            
            return jsonify(return_obj)
        except Error as err:
            print(f"Error: '{err}'")
        finally:
            cur.close() 
            connection.close()
    else: return "No username or no password"

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
