def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")


create_baseball_card_table = """
CREATE TABLE baseball_card (
  baseball_card_id INT PRIMARY KEY,
  first_name VARCHAR(40) NOT NULL,
  last_name VARCHAR(40) NOT NULL,
  year VARCHAR(4) NOT NULL,
  brand VARCHAR(20) NOT NULL,
  card_number VARCHAR(10) NOT NULL,
  description VARCHAR(100) NOT NULL,
  card_condition VARCHAR(20) NOT NULL,
  buy_price DECIMAL(14,2) default NULL,
  buy_date DATE default NULL,
  sell_price DECIMAL(14,2) default NULL,
  sell_date DATE default NULL,
  profit_loss DECIMAL(14,2) default NULL
  );
"""

q1 = """
SELECT * FROM baseball_card;
"""

# results = read_query(connection, q1)

# Returns a list of lists and then creates a pandas DataFrame
# from_db = []

# for result in results:
#   result = list(result)
#   from_db.append(result)


# columns = ["index", "first_name", "last_name", "year", "brand", "card_number", "description", "card_condition", "buy_price", "buy_date", "sell_price", "sell_date", "profit_loss"]
# df = pd.DataFrame(from_db, columns=columns)
# df.style
# execute_query(connection, print_all_baseball_cards)
# create_database_query = "CREATE DATABASE card_inventory_db"

# create_database(connection, create_database_query)