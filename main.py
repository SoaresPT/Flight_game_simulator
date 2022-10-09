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
        raise Exception(f'Section {0} not found in the {1} file'.format(section, filename))
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


def print_airports_single_line(airport_list: list):
    airports_str = ""
    for index, tup in enumerate(airport_list):
        airports_str += f"{tup[0]}, {tup[1]} || "
    return airports_str[0:-2]

# Find airports nearby


def airports_nearby():
    reachable_airports = []
    nearby = f"SELECT * from airport where city != '{current_location[-1]}';"
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
    all_places_visited.append(current_city_country)
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


# def search_username():
#     try:
#         select_id_from_username_query = f"SELECT id FROM player WHERE username = '{username}'"
#         cur.execute(select_id_from_username_query)
#         username_row = cur.fetchall()
#         return len(username_row) # returns how many results the query returned
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)


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


def test_ascii():
    user = username + (" " * (20 - len(username)))
    print(f"""\
        .----.                                                   .'.
        |  /   '                                                 |  '
        |  |    '                                                '  :
        |  |     '             .-~~~-.               .-~-.        \ |
        |  |      '          .\\   .//'._+_________.'.'  /_________\|
        |  |___ ...'.__..--~~ .\\__//_.-     . . .' .'  /      :  |  `.
        |.-"  .'  /                          . .' .'   /.      :_.|__.'
       <    .'___/    {user}   .' .'    /|.      : .'|\\
        ~~--..                             .' .'     /_|.      : | | \\
          /_.' ~~--..__             .----.'_.'      /. . . . . . | |  |
                      ~~--.._______'.__.'  .'      /____________.' :  /
                               .'   .''.._'______.'                '-'
                               '---'
                               """)


#def all_cities_visited():


if __name__ == "__main__":
    # Vars initialization
    total_turns = 0
    co2_wasted = 0 # Need to find a way to calculate this
    all_places_visited = []
    flight_range = 800

    # Call login screen at the start of the game
    login_screen()
    #test_ascii()
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
    add_username(username)
    print(f"Welcome, {username}!")
    test_ascii()

    # Populate the current_location - Currently will always be Helsinki
    current_location = starting_location()
    current_city_country = f"{current_location[-1]}, {current_location[-2]}"
    print(f"You are a new pilot in the FedEx."
          f"\nYour mission is to deliver packages to the following airports.\n"
          f"You are flying Boeing 737-400 with the fuel limited to {flight_range} km.\n"
          f"If you can't reach your target destination directly, you have to fly by cities that are on the way,"
          f" and refill the fuel tank.\n"
          f"Try using most efficient roots in order to generate less carbon footprint &"
          f" save company's operational costs.\n"
          f"You starting position is {current_city_country}. Good luck!")
    print(f"Reach these airports in any order:")
    # Grab the 5 closest airports to the current location
    generated_5_airports = get_random_airports()
    print_airports(generated_5_airports)
    print("\n")

    print(f"From {current_city_country} can travel to any of these airports:")

    while len(generated_5_airports) > 0:
        nearby_airports = airports_nearby()
        destination = flight_target(nearby_airports)
        current_city_country = f"{destination[-1]},{destination[-2]}"
        current_location = destination
        update_curr_location()
        total_turns += 1
        print(f"You're now in {current_city_country}.")
        if current_city_country not in generated_5_airports:
            print(f"You need to deliver your package to the following airport(s) "
              f"in: {print_airports_single_line(generated_5_airports)}\n")
        # Uncomment when debugging if needed - Remove later
        #print(generated_5_airports)

        # Edit this later to make it less sphagetti - Leaving this now for future debugging purposes
        if (current_location[-1], current_location[-2]) in generated_5_airports:
            print(f"Nicely done! You have delivered your package to one of your destinations {current_city_country}.")
            generated_5_airports.remove((current_location[-1], current_location[-2]))
            print(f"You have the following destinations left:\n")
            print_airports(generated_5_airports)
    print(f"Congratulations!! You finished the game!")
    print(f" You have visited:{', '.join(all_places_visited)}")
    print(all_places_visited)
    print(f"It took you {total_turns} turns to deliver all the packages. The total CO2 wasted was {co2_wasted}")



    # forcefully closing this to be 100% sure no connection gets stuck
    closeDBConnection()