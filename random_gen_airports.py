import random
import main
import psycopg2


def get_random_airports():
    airports_list = []
    while len(airports_list) < 5:
        sql_DB_length = f"SELECT city FROM airport WHERE id = '{random.randint(1, 42)}';"
        conn = psycopg2.connect()

        # create a cursor
        cur = conn.cursor()
        cur.execute(sql_DB_length)
        result = cur.fetchall()
        airports_list.append(result[0][0])
    return airports_list


