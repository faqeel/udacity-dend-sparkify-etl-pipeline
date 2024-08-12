import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_staging_tables(cur, conn):
    for query in copy_table_queries:
        try:
            cur.execute(query)
            conn.commit()
            logging.info(f"Successfully executed staging query: {query[:50]}...")  # Log first 50 chars of query
        except psycopg2.Error as e:
            logging.error(f"Error loading staging table: {e}")
            conn.rollback()


def insert_tables(cur, conn):
    for query in insert_table_queries:
        try:
            cur.execute(query)
            conn.commit()
            logging.info(f"Successfully executed insert query: {query[:50]}...")  # Log first 50 chars of query
        except psycopg2.Error as e:
            logging.error(f"Error inserting data: {e}")
            conn.rollback()


def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    try:
        conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
        cur = conn.cursor()
        logging.info("Connected to the database")

        load_staging_tables(cur, conn)
        logging.info("Finished loading data into staging tables")

        insert_tables(cur, conn)
        logging.info("Finished inserting data into analytics tables")

        cur.close()
        conn.close()
        logging.info("ETL process completed. Database connection closed.")
    except psycopg2.Error as e:
        logging.error(f"Error connecting to the database: {e}")


if __name__ == "__main__":
    main()