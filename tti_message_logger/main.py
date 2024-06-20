import os
import threading

from database.db import create_db_and_tables
from database.db import db_engine
from dependencies import utility_functions
from dependencies.config import logger_config
from dependencies.config import mqtt_config
from dependencies.config import rabbit_config
from tti_message_logger_service import TtiMessageLoggerService


def main(
        service_logger,
        control_application_queue,
        rabbit_username,
        rabbit_password,
        rabbit_host,
        rabbit_queue_name,
        rabbit_routing_key,
        engine,
        mqtt_pass,
        mqtt_host,
        mqtt_port,
        mqtt_sensor_data_sub_topic,
        mqtt_user_tail,
):
    try:
        service = TtiMessageLoggerService(
            logger=service_logger,
            rabbit_username=rabbit_username,
            rabbit_password=rabbit_password,
            rabbit_host=rabbit_host,
            queue_control_command_name=control_application_queue,
            rabbit_message_queue_name=rabbit_queue_name,
            rabbit_message_routing_key=rabbit_routing_key,
            db_engine=engine,
            mqtt_pass=mqtt_pass,
            mqtt_host=mqtt_host,
            mqtt_port=mqtt_port,
            mqtt_sensor_data_sub_topic=mqtt_sensor_data_sub_topic,
            mqtt_user_tail=mqtt_user_tail,
        )
        start_rabbit_thread = threading.Thread(target=service.start_rabbit)
        start_rabbit_thread.start()

        init_monitoring_thread = threading.Thread(target=service.init_start_monitoring)
        init_monitoring_thread.start()

    except Exception as e:
        service_logger.exception("Error occurred while initializing event receiver: %s", str(e))


if __name__ == "__main__":
    logger = utility_functions.get_logger(logger_config)
    try:
        create_db_and_tables(db_engine)
        main(
            logger,
            os.getenv("CONTROL_APPLICATION_QUEUE"),
            rabbit_config.credentials_username,
            rabbit_config.credentials_password,
            rabbit_config.host_rabbit,
            rabbit_config.queue_name,
            rabbit_config.routing_key,
            db_engine,
            mqtt_config.mqtt_pass,
            mqtt_config.mqtt_host,
            mqtt_config.mqtt_port,
            mqtt_config.mqtt_sensor_data_sub_topic,
            os.getenv("MQTT_USER_TAIL"),
        )
    except Exception as e:
        logger.error(f"Error occurred while starting the service:  {str(e)}")
