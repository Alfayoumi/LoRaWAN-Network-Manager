import os
import threading

from database.db import create_db_and_tables
from database.db import drop_db_and_tables
from database.db import db_engine
from dependencies import utility_functions
from dependencies.config import logger_config
from dependencies.config import rabbit_config
from stream_event_logger_service import StreamEventLogger

rabbit_username = rabbit_config.credentials_username
rabbit_password = rabbit_config.credentials_password
rabbit_host = rabbit_config.host_rabbit
rabbit_queue_name = rabbit_config.queue_name
rabbit_routing_key = rabbit_config.routing_key

service_logger = utility_functions.get_logger(logger_config)

control_gateways_queue = os.getenv("CONTROL_GATEWAYS_QUEUE", "control_gateways_queue")


def main():
    try:
        service = StreamEventLogger(
            logger=service_logger,
            rabbit_username=rabbit_username,
            rabbit_password=rabbit_password,
            rabbit_host=rabbit_host,
            control_gateways_queue=control_gateways_queue,
            rabbit_message_queue_name=rabbit_queue_name,
            rabbit_message_routing_key=rabbit_routing_key,
            db_engine=db_engine,
        )
        start_rabbit_thread = threading.Thread(target=service.start_rabbit)
        start_rabbit_thread.start()
        init_monitoring_thread = threading.Thread(target=service.init_start_monitoring)
        init_monitoring_thread.start()

    except Exception as e:
        service_logger.exception("Error occurred while initializing event receiver: %s", str(e))


if __name__ == "__main__":
    """
    Drops the database and tables if they exist, creates the database and tables, 
    and starts monitoring for metadata events.
    Then, initializes the event receiver to start receiving metadata events.
    """
    try:
        # drop_db_and_tables(db_engine)
        create_db_and_tables(db_engine)
        main()
    except Exception as e:
        service_logger.error("Error ", repr(e))
