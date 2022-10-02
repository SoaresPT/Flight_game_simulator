import psycopg2
import random
from configparser import ConfigParser
from geopy import distance


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


def connect():

    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        params = config()

        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
################### length of airport table
        # print("Count of Rows")
        cur.execute("SELECT * FROM airport")
        airport_table_length = len(cur.fetchall())
        # print(airport_table_length)

        def default_city():
            start_city = f"SELECT * FROM airport WHERE icao = 'EFHK'";
            cur.execute(start_city)
            result = cur.fetchall()
            return result[0]
        current_city = default_city()
        print(current_city)               #('EFHK', 'Helsinki Vantaa Airport', 60.3172, 24.9633, 179, 'Finland', 'Helsinki')

        def get_random_airports():
            airports_list = []
            while len(airports_list) < 5:
                sql_db_length = f"SELECT city FROM airport WHERE icao = (SELECT icao FROM airport order by random() limit 1);"
                cur.execute(sql_db_length)
                result = cur.fetchall()
# So no target airport will be same as starting one
                if result[0][0] not in airports_list and result[0][0] != current_city[-1]:
                    airports_list.append(result[0][0])
            return airports_list
        generated_5_airports = get_random_airports()
        print(generated_5_airports)             # ['Ljubljana', 'Riga', 'Prague', 'Valletta', 'Fontvieille']

# Find airports nearby
        def airports_nearby():
            flight_range = 400
            reachable_airports = []
            # for i in range(airport_table_length):
            nearby = f"SELECT * from airport where city != '{current_city[-1]}';"  # [(52.3086, 4.76389), (59.4133, 24.8328), (48.1103, 16.5697), (44.0203, 12.6117), (47.4298, 19.2611), (49.0128, 2.55), (43.8246, 18.3315), (55.9726, 37.4146), (52.3514, 13.4939), (45.7429, 16.0688), (52.1657, 20.9671), (50.9014, 4.48444), (38.7813, -9.13592), (35.8575, 14.4775), (55.6179, 12.656), (43.7258, 7.41967), (42.3594, 19.2519), (41.8045, 12.252), (41.9616, 21.6214), (60.1939, 11.1004), (53.8881, 28.04), (53.4213, -6.27007), (49.6233, 6.20444), (42.6967, 23.4114), (59.6519, 17.9186), (42.3386, 1.40917), (56.9236, 23.9711), (37.9364, 23.9445), (44.5711, 26.085), (46.9277, 28.931), (64.13, -21.9406), (50.1008, 14.26), (48.1702, 17.2127), (44.8184, 20.3091), (54.6341, 25.2858), (51.5053, 0.055278), (50.345, 30.8947), (41.4147, 19.7206), (46.9141, 7.49715), (46.2237, 14.4576), (40.4719, -3.56264)]
            cur.execute(nearby)
            result = cur.fetchall()
            for coords in result:
                if distance.distance(coords[2:4], current_city[2:4]).km < flight_range:
                    reachable_airports.append(coords)
            return reachable_airports
        cities_within_range = airports_nearby()
        print(cities_within_range)

# add debug if number out of the list. Later on
        def flight_target():
            print("Select destination: ")
            for i in range(len(cities_within_range)):
                print(f"\t{i+1} - {cities_within_range[i][-1]}")
            user_choice = int(input("> "))
            target_city = cities_within_range[user_choice-1]
            return target_city
            #print(f'Target city - {target_city}')
        next_dest = flight_target()
        print(next_dest)

# updating DB. With manual id. Need to adjust to pick dynamically username from current player
# Not working. Need to consider ho to fix the updating of current location of the user
        def update_curr_location():
            current = f"UPDATE player SET curr_location = '{next_dest[-1]}' WHERE username LIKE '%Sergio%';"
            cur.execute(current)
            #cur.fetchall()
            get_info = f"SELECT * from player WHERE username = 'Sergio';"
            cur.execute(get_info)
            conn.commit()
            res = cur.fetchall()
            print(res)
            return res

        update_curr_location()









        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


connect()
