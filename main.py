import psycopg2
from psycopg2 import extensions
from configparser import ConfigParser
import sys
from geopy import distance

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

def get_random_airports():
    airports_list = []
    while len(airports_list) < 5:
        sql_db_length = f"SELECT city, country FROM airport WHERE icao = (SELECT icao FROM airport order by random() limit 1);"
        cur.execute(sql_db_length)
        result = cur.fetchall()
        # Generate X number of random airports. Make sure it's not a repeated one and different than the starting location
        if result[0] not in airports_list and result[0][0] != current_location[-1]:
            airports_tuple = (result[0][0], result[0][1])
        else:
            continue
        airports_list.append(airports_tuple)
    return airports_list

# Iterate and print the list of airports the user must travel to. This outputs in a nicer format the contents of get_random_airports()
def print_airports(airport_list: list):
    for index, tup in enumerate(airport_list):
        print(f"\t{tup[0]}, {tup[1]}")

# Find airports nearby
def airports_nearby():
    flight_range = 800
    reachable_airports = []
    # for i in range(airport_table_length):
    nearby = f"SELECT * from airport where city != '{current_location[-1]}';"  # [(52.3086, 4.76389), (59.4133, 24.8328), (48.1103, 16.5697), (44.0203, 12.6117), (47.4298, 19.2611), (49.0128, 2.55), (43.8246, 18.3315), (55.9726, 37.4146), (52.3514, 13.4939), (45.7429, 16.0688), (52.1657, 20.9671), (50.9014, 4.48444), (38.7813, -9.13592), (35.8575, 14.4775), (55.6179, 12.656), (43.7258, 7.41967), (42.3594, 19.2519), (41.8045, 12.252), (41.9616, 21.6214), (60.1939, 11.1004), (53.8881, 28.04), (53.4213, -6.27007), (49.6233, 6.20444), (42.6967, 23.4114), (59.6519, 17.9186), (42.3386, 1.40917), (56.9236, 23.9711), (37.9364, 23.9445), (44.5711, 26.085), (46.9277, 28.931), (64.13, -21.9406), (50.1008, 14.26), (48.1702, 17.2127), (44.8184, 20.3091), (54.6341, 25.2858), (51.5053, 0.055278), (50.345, 30.8947), (41.4147, 19.7206), (46.9141, 7.49715), (46.2237, 14.4576), (40.4719, -3.56264)]
    cur.execute(nearby)
    result = cur.fetchall()
    for coords in result:
        if distance.distance(coords[2:4], current_location[2:4]).km < flight_range:
            reachable_airports.append(coords)
    return reachable_airports

# add debug if number out of the list. Later on
def flight_target(airports: list):
    print("Select destination: ")
    for i in range(len(airports)):
        print(f"\t{i+1} - {airports[i][-1]}, {airports[i][-2]}")
    while True:
        try:
            user_choice = int(input("> "))
        except ValueError:
            print("Invalid input. Input a airport number from the list above.")
            continue
        else:
            if user_choice <= 0 or user_choice > len(airports):
                print("The selected airport is not valid!")
                continue
        break
    target_city = airports[user_choice-1]
    return target_city

def update_curr_location():
    current = f"UPDATE player SET curr_location = '{current_city_country}' WHERE username = '{username}';"
    cur.execute(current)
    get_info = f"SELECT * from player WHERE username = '{username}';"
    cur.execute(get_info)
    conn.commit()
    res = cur.fetchall()
    return res

def starting_location():
    global current_location
    start_city_query = f"SELECT * FROM airport WHERE icao = 'EFHK';"
    cur.execute(start_city_query)
    result = cur.fetchall()
    current_location = result[0]
    return current_location

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
        print(f"{username} has been added to the database!")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def login_screen():
    print("\t\t-- Flight Game --")
    print("\t\t[1] Create new game")
    print("\t\t[2] Exit")

if __name__ == "__main__":
    login_screen()

    # Main Menu Selection
    option = input("Type your choice: ")
    while True:
        if option == "1":
            # Ask user to type a username
            while True:
                username = input("Type your username: ").capitalize()
                if len(username) == 0:
                    print("Username cannot be empty!")
                    continue
                if len(username) > 20:
                    print(f"Your username is too long! Please use at most 20 characters for your username.")
                    continue
                break
            break
        elif option == "2":
            print("Thank you for playing!")
            sys.exit(1)
        else:
            option = input("Invalid choice. Please type your choice again: ")
    
    # Connect to the DB after the user selects the nickname
    connectDB()

    # Add new user to the DB or greet an old user
    if search_username() == 0:
        print("Adding new user to the database...")
        add_username(username)
        print(f"Welcome, {username}!")
    else:
        print(f"Welcome back, {username}!")
    
    # Populate the current_location - Currently will always be Helsinki
    current_location = starting_location()
    current_city_country = f"{current_location[-1]}, {current_location[-2]}"
    print(f"Your mission is to deliver packages to the following airports. You starting position is {current_city_country}. Good luck!")
    print(f"Reach these airports by any order:")
    # Grab the 5 closest airports to the current location
    generated_5_airports = get_random_airports()
    print_airports(generated_5_airports)
    print("\n")

    print("You are flying a small place and so you have limited fuel. You can travel to any of these airports to refuel:")

    while len(generated_5_airports) > 0:
        nearby_airports = airports_nearby()
        destination = flight_target(nearby_airports)
        current_city_country = f"{destination[-1]}, {destination[-2]}"
        current_location = destination
        update_curr_location()
        print(f"You're now in {current_city_country}")


    
    # forcefully closing this to be 100% sure no connection gets stuck 
    closeDBConnection()
    """
    This will remove a city, country from the list of tuples - TO DO LATER
    """
    #generated_5_airports.remove(("Vienna", "Austria"))
    #print(generated_5_airports)