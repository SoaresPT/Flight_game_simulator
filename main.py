import psycopg2
import random
from configparser import ConfigParser


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

        def get_random_airports():
            airports_list = []
            while len(airports_list) < 5:
                sql_db_length = f"SELECT city FROM airport WHERE id = '{random.randint(1, 42)}';"
                cur.execute(sql_db_length)
                result = cur.fetchall()
                if result[0][0] not in airports_list:
                    airports_list.append(result[0][0])
            return airports_list
        generated_5_airports = get_random_airports()
        print(generated_5_airports)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


connect()