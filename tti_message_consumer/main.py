import logging

from database.db import create_db_and_tables
from database.db import db_engine
from tti_message_consumer_service import tti_message_consumer

if __name__ == "__main__":
    try:
        create_db_and_tables(db_engine)
        tti_message_consumer()
    except Exception as e:
        logging.error(f"Error during in the mian function: {repr(e)}")
