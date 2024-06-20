import logging

from database.db import create_db_and_tables, db_engine
from dependencies import utility_functions
from dependencies.config import logger_config, rabbit_config
from stream_event_consumer_service import MessageConsumer

threading_numbers = 10


def main():
    # Read configuration values from the config file

    # Extract rabbitmq connection details from the config file
    rabbit_username = rabbit_config.credentials_username
    rabbit_password = rabbit_config.credentials_password
    rabbit_host = rabbit_config.host_rabbit
    consumer_queue_name = rabbit_config.queue_name

    # Set up a logger for the consumer
    consumer_logger = utility_functions.get_logger(logger_config)

    # Create a message consumer instance with the extracted configuration details
    metadata_consumer = MessageConsumer(
        consumer_logger,
        rabbit_username,
        rabbit_password,
        rabbit_host,
        consumer_queue_name,
        db_engine,
        threading_numbers,
    )

    # Start the RabbitMQ consumer
    try:
        metadata_consumer.start_consuming()
    except Exception as e:
        consumer_logger.error(f"Error occurred while starting RabbitMQ consumer: {e}")
        raise e


if __name__ == "__main__":
    try:
        create_db_and_tables(db_engine)
        main()
    except Exception as e:
        logging.error(f"Error during setup: {e}")
