import psycopg2
from psycopg2 import extensions
from configparser import ConfigParser
import sys


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

def search_username():
    try:
        select_username_query = f"SELECT username FROM player WHERE username = {username}"
        cur.execute(select_username_query)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)    

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
        
    connectDB()

    # Greet new/old user
    select_id_from_username_query = f"SELECT id FROM player WHERE username = '{username}'"
    cur.execute(select_id_from_username_query)
    username_row = cur.fetchall()
    if len(username_row) == 0:
        print("Adding new user to the database...")
        add_new_user = f"INSERT INTO player(username) VALUES ('{username}')"
        cur.execute(add_new_user)
        conn.commit()
        print(f"Welcome, {username}!")
    else:
        print(f"Welcome back, {username}!")
        
    closeDBConnection()
    #print("Closed connection")