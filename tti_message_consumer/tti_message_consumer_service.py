import concurrent.futures
import json

import pika
from sqlmodel import Session
from sqlmodel import select

from database.db import db_engine
from dependencies import utility_functions
from dependencies.config import logger_config
from dependencies.config import rabbit_config
from dependencies.exceptions import RabbitMQConnectionError, RabbitMQConsumingError, DatabaseError, ProcessError
from tti_message_consumer.database.models import AllRelation
from tti_message_consumer.database.models import TTIUplinkMessage

tti_message_logger = utility_functions.get_logger(logger_config)
# Extract rabbitmq connection details from the config file
rabbit_username = rabbit_config.credentials_username
rabbit_password = rabbit_config.credentials_password
rabbit_host = rabbit_config.host_rabbit
consumer_queue_name = rabbit_config.queue_name
num_tx_replica = 3
num_of_threads = 5


class TtiMessageConsumer:
    def __init__(
            self,
            logger,
            rabbit_username,
            rabbit_password,
            rabbit_host,
            queue_name,
            db_engine,
            max_threads,
    ):
        self.logger = logger
        self.credentials = pika.PlainCredentials(username=rabbit_username, password=rabbit_password)
        self.parameters = pika.ConnectionParameters(
            host=rabbit_host,
            credentials=self.credentials,
        )
        self.queue_name = queue_name
        self.db_engine = db_engine
        self.connection = None
        self.channel = None
        self.max_threads = max_threads
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads)

    def start_consuming(self):
        try:
            self.connection = pika.BlockingConnection(self.parameters)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            self.channel.basic_qos(prefetch_count=1)
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise RabbitMQConnectionError("Failed to connect to RabbitMQ.") from e

        try:

            for _ in range(self.max_threads):
                self.channel.basic_consume(
                    queue=self.queue_name, on_message_callback=self.on_message_received
                )
            self.channel.start_consuming()
        except Exception as e:
            self.logger.error(f"RabbitMQ channel was closed: {repr(e)}")
            raise RabbitMQConsumingError(f"Error starting RabbitMQ consumer: {repr(e)}") from e

    def on_message_received(self, channel, method, properties, body):
        # self.logger.debug("Received message from queue")
        try:
            message = json.loads(body)
            self.thread_pool.submit(self.process_message, message)
        except Exception as e:
            self.logger.error(f"{repr(e)}")
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    def get_device_relation(self, dev_addr, gateway_tti_id):
        try:
            with Session(self.db_engine) as session:
                self.logger.debug(f"update_or_add_end_device_relation")
                statement = select(AllRelation).where(
                    AllRelation.dev_addr == dev_addr,
                    AllRelation.gateway_tti_id == gateway_tti_id,
                )
                return session.exec(statement).all()
        except Exception as e:
            self.logger.error(f"Error in get_device_relation: {str(e)}")
            raise DatabaseError("get_device_relation ",
                                f"Error in get_device_relation: {str(e)}")

    def update_or_add_end_device_relation(
            self, device_id, dev_addr, last_f_cnt, gateway_tti_id, application_id
    ):
        end_device_relation = {
            "device_id": device_id,
            "dev_addr": dev_addr,
            "last_f_cnt": last_f_cnt,
            "gateway_tti_id": gateway_tti_id,
            "application_id": application_id,
        }

        try:
            with Session(self.db_engine) as session:
                self.logger.debug(f"update_or_add_end_device_relation")
                existing_metadata = self.get_device_relation(dev_addr, gateway_tti_id)
                if not existing_metadata:
                    self.store_data(AllRelation(**end_device_relation))
                else:
                    # Update the last_f_cnt of the row with matching device_id and application_id
                    for metadata in existing_metadata:
                        if metadata.device_id == device_id and metadata.application_id == application_id:
                            metadata.last_f_cnt = last_f_cnt
                            session.add(metadata)
                            session.commit()
                            break
                    else:
                        self.store_data(AllRelation(**end_device_relation))
        except DatabaseError:
            raise
        except Exception as e:
            self.logger.error(f"Error in update_or_add_end_device_relation: {str(e)}")
            raise DatabaseError("update_or_add_end_device_relation ",
                                f"Error in update_or_add_end_device_relation: {str(e)}")

    def process_message(self, message):
        try:
            packet_rx_data = TTIUplinkMessage.from_json(message)
            for gw_data in packet_rx_data.rx_metadata:
                self.update_or_add_end_device_relation(
                    packet_rx_data.device_id,
                    packet_rx_data.dev_addr,
                    packet_rx_data.f_cnt,
                    gw_data.gateway_ids.gateway_id,
                    packet_rx_data.application_id,
                )
        except DatabaseError:
            raise
        except Exception as e:
            self.logger.error(f"Failed to parse message in process_message: {str(e)}")
            raise ProcessError(f"Error process_message: {repr(e)}") from e

    def store_data(self, data) -> None:
        """
        Stores the given data object in the database by adding it to the session
        and committing the transaction.

        Args:
            data: The data object to be stored.

        Returns:
            None
        """
        with Session(self.db_engine) as session:
            try:
                session.add(data)
                session.commit()
                self.logger.debug("Data stored successfully in the database.")
            except Exception as e:
                self.logger.error(f"Error storing data in the database store_data: {str(e)}")
                raise DatabaseError("store_data ",
                                    f"Error storing data in the database store_data: {str(e)}")


def tti_message_consumer():
    tti_msg_consumer = TtiMessageConsumer(
        tti_message_logger,
        rabbit_username,
        rabbit_password,
        rabbit_host,
        consumer_queue_name,
        db_engine,
        num_of_threads,
    )
    tti_msg_consumer.start_consuming()
