import psycopg2
from psycopg2 import extensions
from configparser import ConfigParser
import sys
import os
import time
from geopy import distance
import colorama
from colorama import Fore, Back, Style

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


def connect_db():
    # global variables to keep connection open and cursor queries inside functions
    global conn
    global cur
    """ Connect to the PostgresSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgresSQL server
        print(f'{Fore.LIGHTBLUE_EX}Connecting to the game database...')
        try:
            conn = psycopg2.connect(**params)
        except psycopg2.OperationalError as e:
            print(f'{Fore.RED}Error: {e}')
            sys.exit(1)
        # Test if connection was successful
        if conn.status == extensions.STATUS_READY:
            print(f"{Fore.LIGHTGREEN_EX}Successfully connected to the game server!\n\n")
        else:
            print(f"{Fore.RED}Error connecting to the database. Cannot start the game.")
            sys.exit(1)
        # create a cursor
        cur = conn.cursor()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def get_random_airports():
    airports_list = []
    while len(airports_list) < 5:
        sql_db_length = f"SELECT city, country FROM airport WHERE icao = " \
                        f"(SELECT icao FROM airport order by random() limit 1);"
        cur.execute(sql_db_length)
        result = cur.fetchall()
        # Generate X number of random airports. Make sure it's not a repeated and different from the starting location
        if result[0] not in airports_list and result[0][0] != current_location[-1]:
            airports_tuple = (result[0][0], result[0][1])
        else:
            continue
        airports_list.append(airports_tuple)
    return airports_list


# Iterate and print the list of airports the user must travel to.
# This outputs in a nicer format the contents of get_random_airports()
def print_airports(airport_list: list):
    airports_str = ""
    for index, tup in enumerate(airport_list):
        airports_str += f"{Fore.LIGHTRED_EX}{tup[0]}, {tup[1]} {Fore.LIGHTWHITE_EX}|| "
    print(airports_str[0:-3])


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

def flight_target(airports: list):
    print("")
    print(f"{Fore.LIGHTWHITE_EX}Select your next destination: ")
    for i in range(len(airports)):
        print(f"{Fore.LIGHTGREEN_EX}\t{i + 1} - {airports[i][-1]}, {airports[i][-2]}")
    while True:
        try:
            user_choice = int(input("> "))
        except ValueError:
            print(f"{Fore.LIGHTRED_EX}Invalid input. Input a airport number from the list above.")
            continue
        else:
            if user_choice <= 0 or user_choice > len(airports):
                print(f"{Fore.LIGHTRED_EX}The selected airport is not valid!")
                continue
        break
    target_city = airports[user_choice - 1]
    return target_city


def update_curr_location():
    current = f"UPDATE player SET curr_location = '{current_city_country}' WHERE username = '{username}';"
    cur.execute(current)
    insert_game_turn_query = f"INSERT INTO GAME(game_id, player_id, city_visited)" \
                             f" VALUES ({game_id}, {player_id}, '{current_city_country}')"
    cur.execute(insert_game_turn_query)
    all_places_visited.append(current_city_country)
    get_info = f"SELECT * from player WHERE username = '{username}';"
    cur.execute(get_info)
    conn.commit()
    res = cur.fetchall()
    return res


def total_travel_distance(airport_from, airport_to):
    dist = distance.distance(airport_from, airport_to).km
    return dist


def co2_calculator(target_cities_list: list):
    co2_packages_left = {
        1: 8.24,
        2: 16.62,
        3: 25,
        4: 33.24,
        5: 41.62
    }
    list_length = len(target_cities_list)
    if list_length in co2_packages_left:
        co2_per_journey = co2_packages_left[list_length] * total_travel_distance(travel_from, travel_to)
    return co2_per_journey


def co2_per_trip(target_cities_list: list):
    co2_packages_left = {
        1: 8.24,
        2: 16.62,
        3: 25,
        4: 33.24,
        5: 41.62
    }
    list_length = len(target_cities_list)
    return co2_packages_left.get(list_length)


def starting_location():
    global current_location
    start_city_query = f"SELECT * FROM airport WHERE icao = 'EFHK';"
    cur.execute(start_city_query)
    result = cur.fetchall()
    current_location = result[0]
    return current_location


def get_game_id():
    game_id_query = f"SELECT MAX(game_id) from game;"
    cur.execute(game_id_query)
    game_id = cur.fetchone()
    if game_id[0] is None:  # If there's no records on the table
        game_id = 1
    else:
        game_id = game_id[0] + 1
    return game_id


def get_player_id():
    player_id_query = f"SELECT id from player where username ='{username}'"
    cur.execute(player_id_query)
    player_id = cur.fetchone()
    return player_id[0]


def close_db_connection():
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
        return len(username_row)  # returns how many results the query returned
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def add_username(username: str):
    try:
        add_new_user = f"INSERT INTO player(username) VALUES ('{username}')"
        cur.execute(add_new_user)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"{Fore.RED}{error}")


def login_screen():
    print(f"\t\t{Fore.LIGHTWHITE_EX}-- Flight Game --")
    print(f"\t\t{Fore.LIGHTWHITE_EX}[1] Create new game")
    print(f"\t\t{Fore.LIGHTWHITE_EX}[2] Exit")


def welcome_ascii():
    user = username + (" " * (20 - len(username)))
    print(f"""\
        {Fore.BLUE}
        .----.                                                   .'.
        |  /   '                                                 |  '
        |  |    '                                                '  :
        |  |     '             .-~~~-.               .-~-.        \ |
        |  |      '          .\\   .//'._+_________.'.'  /_________\|
        |  |___ ...'.__..--~~ .\\__//_.-     . . .' .'  /      :  |  `.
        |.-"  .'  /  {Fore.GREEN}Welcome Pilot{Fore.BLUE}           . .' .'   /.      :_.|__.'
       <    .'___/    {Fore.YELLOW}{user}{Fore.BLUE}   .' .'    /|.      : .'|\\
        ~~--..                             .' .'     /_|.      : | | \\
          /_.' ~~--..__             .----.'_.'      /. . . . . . | |  |
                      ~~--.._______'.__.'  .'      /____________.' :  /
                               .'   .''.._'______.'                '-'
                               '---'
                               """)


def landing_ascii():
    print(f"""{Fore.LIGHTWHITE_EX}
          */ | \*
          / -+- \\
      ---o--(_)--o---
        /  0 " 0  \\
      */     |     \*
      /      |      \\
""")


def small_airplane():
    for i in range(0, 5):
        print(f"{Fore.LIGHTWHITE_EX}Flying to {Fore.LIGHTGREEN_EX}{current_city_country}")
        print(f'''{Fore.LIGHTWHITE_EX}
        
{i * "                    "}              _
{i * "                    "}            -=\`\\
{i * "                    "}        |\ ____\_\__
{i * "                    "}    -=\c`""""""" "` )
{i * "                    "}        `~~~~~/ /~~`
{i * "                    "}            -==/ /
{i * "                    "}              '-'
        ''')
        time.sleep(0.6)
        clear_screen()


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')  # cross-platform clear screen


def convert_list_to_dict(final: list):
    for value in final:
        split_total = value.split(',')
        cities.append(split_total[0])
        countries.append(split_total[1])
    dict_countries = {i: countries.count(i) for i in countries}
    return dict_countries


def print_total_visited(dict_countries):
    for country, num_of_visits in dict_countries.items():
        if num_of_visits > 1:
            print(f"{Fore.LIGHTGREEN_EX}{country}{Fore.LIGHTWHITE_EX} - {num_of_visits} times")
        else:
            print(f"{Fore.LIGHTGREEN_EX}{country}")


def bonus(total_co2):
    if total_co2 < 100:
        paint_output = Fore.LIGHTGREEN_EX
        output_msg = "Great job! You are getting a performance bonus that you deserve."
    else:
        paint_output = Fore.LIGHTRED_EX
        output_msg = "Your carbon footprint is higher than listed in the KPI so try choosing more efficient routes" \
                     " in future in order to get a bonus."

    print(f"{Fore.LIGHTWHITE_EX}The total carbon emission is {paint_output}{total_co2:.2f} kg CO2")
    print(f"{Fore.LIGHTWHITE_EX}{output_msg}\n")


if __name__ == "__main__":
    # Vars initialization
    total_turns = 0
    total_co2_wasted = 0.0
    all_places_visited = []
    cities = []
    countries = []
    flight_range = 800
    total_dist = 0.0
    co2_bonus_limit = 100_000
    colorama.init(autoreset=True)

    # Call login screen at the start of the game
    login_screen()
    # Main Menu Selection
    option = input(f"{Fore.LIGHTWHITE_EX}Type your choice: ")
    while True:
        if option == "1":
            # Ask user to type a username
            while True:
                username = input(f"{Fore.LIGHTWHITE_EX}Type your username: ").capitalize()
                if len(username) == 0:
                    print(f"{Fore.RED}Username cannot be empty!")
                    continue
                if len(username) > 20:
                    print(f"{Fore.RED}Your username is too long! Please use at most 20 characters for your username.")
                    continue
                break
            break
        elif option == "2":
            print("Thank you for playing!")
            sys.exit(1)
        else:
            option = input("Invalid choice. Please type your choice again: ")

    # Connect to the DB after the user selects the nickname
    connect_db()

    # Add new user to the DB if it doesn't exist
    if search_username() == 0:
        add_username(username)

    # Grab current player ID and assign a new game_id for this session so we can log the player's movements
    game_id = get_game_id()
    player_id = get_player_id()
    welcome_ascii()
    time.sleep(2)
    # Populate the current_location - Currently will always be Helsinki
    current_location = starting_location()
    generated_5_airports = get_random_airports()
    current_city_country = f"{current_location[-1]}, {current_location[-2]}"
    print(f"{Fore.LIGHTWHITE_EX}You are a new pilot of FedEx.")
    time.sleep(2)
    print(f"{Fore.LIGHTWHITE_EX}Your mission is to deliver packages to the airports listed in your flight task.")
    time.sleep(2)
    print(f"{Fore.LIGHTWHITE_EX}You are flying a {Fore.LIGHTGREEN_EX}Boeing 737-400{Fore.LIGHTWHITE_EX} with "
          f"the payload of {Fore.LIGHTGREEN_EX}23.000 kg{Fore.LIGHTWHITE_EX} and flight range is restricted "
          f"to {Fore.LIGHTGREEN_EX}{flight_range} km{Fore.LIGHTWHITE_EX} due to fuel constrains.")
    time.sleep(2)
    print(f"{Fore.LIGHTWHITE_EX}If you can't reach your target destination directly, you have to fly to cities that"
          f" are on the way, and refill the fuel tank.")
    time.sleep(2)
    print(f"{Fore.LIGHTWHITE_EX}Try using the most efficient routes in order to generate less carbon footprint &"
          f" save company's operational costs.")
    time.sleep(2)
    print(f"{Fore.LIGHTWHITE_EX}From your starting point you are leaving fully loaded with cargo, and your CO2 emission"
          f" is {Fore.LIGHTRED_EX}{co2_per_trip(generated_5_airports)} kg{Fore.LIGHTWHITE_EX} per km.")
    time.sleep(2)
    print(f"{Fore.RED}{Style.BRIGHT}HINT: The fewer packages you carry, the less CO2 emission you generate!")
    time.sleep(2)
    print(f"{Fore.LIGHTWHITE_EX}Last but not least, if your total carbon footprint after you deliver your last package"
          f" is under{Fore.LIGHTGREEN_EX} 100.000 kg CO2{Fore.LIGHTWHITE_EX}, you will get a bonus!\n")
    time.sleep(2)
    print(f"{Fore.LIGHTWHITE_EX}You starting position is {Fore.LIGHTGREEN_EX}{current_city_country}{Fore.LIGHTWHITE_EX}."
          f" Good luck & have fun!")
    time.sleep(2)
    print(f"{Fore.LIGHTWHITE_EX}Reach these airports in any order:")
    # Grab the 5 closest airports to the current location
    print_airports(generated_5_airports)
    time.sleep(2)
    print("")

    print(f"{Fore.LIGHTWHITE_EX}From {Fore.LIGHTGREEN_EX}{current_city_country}{Fore.LIGHTWHITE_EX} can travel"
          f" to any of these cities:")

    while len(generated_5_airports) > 0:
        nearby_airports = airports_nearby()
        travel_from = [current_location[2], current_location[3]]
        destination = flight_target(nearby_airports)
        travel_to = [destination[2], destination[3]]
        current_city_country = f"{destination[-1]}, {destination[-2]}"
        current_location = destination
        update_curr_location()
        co2_calculator(generated_5_airports)
        total_co2_wasted += co2_calculator(generated_5_airports)
        total_dist += total_travel_distance(travel_from, travel_to)
        total_turns += 1
        small_airplane()
        landing_ascii()
        print(f"{Fore.LIGHTWHITE_EX}You're now in {Fore.LIGHTGREEN_EX}{current_city_country}.\n")
        for city_from_gen_list in generated_5_airports:
            if (current_location[-1], current_location[-2]) in generated_5_airports:
                generated_5_airports.remove((current_location[-1], current_location[-2]))
                if len(generated_5_airports) == 0:
                    break
                print(f"{Fore.LIGHTWHITE_EX}Nicely done!")
                time.sleep(1)
                print(f"{Fore.LIGHTWHITE_EX}You have delivered a package to {Fore.LIGHTBLUE_EX}"
                      f"{current_location[-1]}{Fore.LIGHTWHITE_EX} - one of your target destinations.")
                time.sleep(1)
                print(f"{Fore.LIGHTWHITE_EX}Now you dropped some cargo so your CO2 emission decreased to"
                      f" {Fore.LIGHTRED_EX}{co2_per_trip(generated_5_airports)} kg {Fore.LIGHTWHITE_EX}per km.")
                time.sleep(1)
                print(f"{Fore.LIGHTWHITE_EX}You have the following destinations left:")
                print_airports(generated_5_airports)
                print("")
                break
            elif destination[-1] != city_from_gen_list[0]:
                print(f"{Fore.LIGHTWHITE_EX}You need to deliver your package(s) to the following airport(s) in: ")
                print_airports(generated_5_airports)
                break
    print(f"{Fore.LIGHTBLUE_EX}Congratulations!!!")
    time.sleep(1)
    print(f"{Fore.LIGHTWHITE_EX}You have reached your final destination and finished the game!")
    dict_visits = convert_list_to_dict(all_places_visited)
    time.sleep(2)
    print(f"{Fore.LIGHTWHITE_EX}You have visited {Fore.LIGHTGREEN_EX}{len(dict_visits)}{Fore.LIGHTWHITE_EX} countries:")
    print_total_visited(dict_visits)
    time.sleep(2)
    print(f"{Fore.LIGHTWHITE_EX}It took you {Fore.LIGHTGREEN_EX}{total_turns}{Fore.LIGHTWHITE_EX} turns to deliver"
          f" all the packages.")
    time.sleep(2)
    print(f"{Fore.LIGHTWHITE_EX}The total travelled distance is {Fore.LIGHTGREEN_EX}{total_dist:.2f} km")
    time.sleep(2)
    bonus(total_co2_wasted)
    time.sleep(2)
    print(f"{Fore.LIGHTWHITE_EX}Thank you for playing! Hope you enjoyed.")

    # forcefully closing this to be 100% sure no connection gets stuck
    close_db_connection()
