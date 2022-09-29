import psycopg2
from psycopg2 import extensions
from configparser import ConfigParser
import sys
import random

"""
Basic Connection Functions
"""
def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db

def connectDB():
    # global variables to keep connection open and cursor quieries inside functions

    global conn
    global cur
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the game database...')
        try:
            conn = psycopg2.connect(**params)
        except psycopg2.OperationalError as e:
            print(f'Error: {e}')
            sys.exit(1)
        # Test if connection was successful
        if conn.status == extensions.STATUS_READY:
            print("Successfully connected to the game server!\n\n")
        else:
            print("Error connecting to the database. Cannot start the game.")
            sys.exit(1)
        # create a cursor
        cur = conn.cursor()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def closeDBConnection():
    try:
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)    
    finally:
        if conn is not None:
            conn.close()

""" Game Functions """

def search_username():
    try:
        select_id_from_username_query = f"SELECT id FROM player WHERE username = '{username}'"
        cur.execute(select_id_from_username_query)
        username_row = cur.fetchall()
        return len(username_row) # returns how many results the query returned
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)    

def add_username(username: str):
    try:
        add_new_user = f"INSERT INTO player(username) VALUES ('{username}')"
        cur.execute(add_new_user)
        conn.commit()
        return f"{username} has been added to the database!"
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)        

# Get 5 random airports in a list
def get_random_airports():
    airports_list = []
    while len(airports_list) < 5:
        sql_db_length = f"SELECT city FROM airport WHERE id = '{random.randint(1, 42)}';"
        cur.execute(sql_db_length)
        result = cur.fetchall()
        if result[0][0] not in airports_list:
            airports_list.append(result[0][0])
    return airports_list

def login_screen():
    print("\t\t-- Flight Game --")
    print("\t\t[1] Create new game")
    print("\t\t[2] Exit")

if __name__ == "__main__":
    # Print the login screen
    login_screen()
    
    # Main Menu Selection
    option = input("Type your choice: ")
    while True:
        if option == "1":
            # Ask user to type a username
            username = input("Type your username: ").capitalize()
            if len(username) > 20:            
                username = username[:20]
                print(f"Username trimmed to {username}")
            break
        elif option == "2":
            print("Thank you for playing!")
            sys.exit(1)
        else:
            option = input("Invalid choice. Please type your choice again: ")

    # Connect to the DB after user chose to start playing    
    connectDB()

    # Add new user to the DB or greet an old user
    if search_username() == 0:
        print("Adding new user to the database...")
        add_username(username)
        print(f"Welcome, {username}!")
    else:
        print(f"Welcome back, {username}!")
    
    #Generates 5 airports and prints the results...
    print("Generating 5 random airports...")
    generated_5_airports = get_random_airports()
    print(generated_5_airports)
    # Just forcefully closing this to be 100% sure no connection gets stuck but elephantSQL seems to have a very short keep-alive time which can be annoying for production... Let's see
    closeDBConnection()
    #print("Closed connection")