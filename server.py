import mysql.connector
from mysql.connector import Error
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, request, send_from_directory
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


@app.route('/inventorys', methods=['GET'])
def get_inventory():
    try:
        connection = create_db_connection()
        cur = connection.cursor()
        cur.execute("""SELECT * FROM baseball_card""")
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

@app.route('/inventorys/<baseball_card_id>', methods=['DELETE'])
def delete_inventory_item(baseball_card_id):
    try:
        connection = create_db_connection()
        cur = connection.cursor()
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
        ok_happy = cur.execute("""SELECT * FROM baseball_card WHERE baseball_card_id = %(baseball_card_id)s""", { 'baseball_card_id': baseball_card_id })
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

        if len(card_image_front) > 0:
            uploadedResponse = cloudinary.uploader.upload(card_image_front)
            image_front_url = uploadedResponse['url']
        else:
            image_front_url = ""

        if len(card_image_back) > 0:      
            uploadedResponse2 = cloudinary.uploader.upload(card_image_back)
            image_back_url = uploadedResponse2['url']
        else:
            image_back_url = ""

        sqlQuery = """INSERT INTO baseball_card(baseball_card_id, brand, buy_date, buy_price, card_condition, card_number,
        description, first_name, last_name, profit_loss, sell_date, sell_price, year, card_image_front, card_image_back) 
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        bind_data = (baseball_card_id, brand, buy_date, buy_price, card_condition, card_number, description, first_name, last_name, profit_loss, sell_date, sell_price, year, image_front_url, image_back_url)

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
        connection = create_db_connection()
        cur = connection.cursor()
        values = request.get_json()

        brand = values['brand']
        buy_date = values['buy_date']
        buy_price = Decimal(values['buy_price'])
        card_condition = values['card_condition']
        card_number = values['card_number']
        description = values['description']
        first_name = values['first_name']
        last_name = values['last_name']
        sell_date = values['sell_date']
        sell_price = Decimal(values['sell_price'])
        year = values['year']
        profit_loss = (sell_price - buy_price)
        card_image_front = values['card_image_front']
        card_image_back = values['card_image_back']
    
        uploadedResponse = cloudinary.uploader.upload(card_image_front)
        uploadedResponse2 = cloudinary.uploader.upload(card_image_back)
        image_front_url = uploadedResponse['url']
        image_back_url = uploadedResponse2['url']

        sqlQuery = """UPDATE baseball_card SET brand=%s, buy_date=%s, buy_price=%s, card_condition=%s, card_number=%s,
        description=%s, first_name=%s, last_name=%s, profit_loss=%s, sell_date=%s, sell_price=%s, year=%s, card_image_front=%s, card_image_back=%s WHERE baseball_card_id=%s"""
        bind_data = (brand, buy_date, buy_price, card_condition, card_number, description, first_name, last_name, profit_loss, sell_date, sell_price, year, image_front_url, image_back_url, baseball_card_id)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
