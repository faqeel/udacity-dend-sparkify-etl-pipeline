import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def drop_tables(cur, conn):
    for query in drop_table_queries:
        try:
            cur.execute(query)
            conn.commit()
            logging.info(f"Successfully executed: {query}")
        except psycopg2.Error as e:
            logging.error(f"Error dropping table: {e}")
            conn.rollback()


def create_tables(cur, conn):
    for query in create_table_queries:
        try:
            cur.execute(query)
            conn.commit()
            logging.info(f"Successfully executed: {query}")
        except psycopg2.Error as e:
            logging.error(f"Error creating table: {e}")
            conn.rollback()


def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    try:
        conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
        cur = conn.cursor()
        logging.info("Connected to the database")

        drop_tables(cur, conn)
        create_tables(cur, conn)

        cur.close()
        conn.close()
        logging.info("Database connection closed")
    except psycopg2.Error as e:
        logging.error(f"Error connecting to the database: {e}")

if __name__ == "__main__":
    main()