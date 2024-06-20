import json
import threading
import time
import urllib.request
import pika
import os
from sqlmodel import Session
from sqlmodel import select
from database.db import MonitoredGateways
from dependencies.exceptions import RabbitMQConnectionError, RabbitMQConsumingError, DatabaseError

tti_event_url = os.getenv("TTI_EVENT_URL")
tti_auth_token = os.getenv("TTI_AUTH_TOKEN")


def init_get_streaming(gateway_id):
    data_body = '{"identifiers": [{"gateway_ids": {"gateway_id": "' + gateway_id + '"}}]}'
    data = bytes(data_body, "utf-8")
    headers = {
        "Authorization": tti_auth_token,
        "Accept": "text/event-stream",
        "Content-Type": "text/event-stream",
    }
    return urllib.request.Request(url=tti_event_url, data=data, headers=headers, method="POST")


class MessageSubscriptor(threading.Thread):
    def __init__(
            self,
            logger,
            gateway_id,
            rabbit_username,
            rabbit_password,
            rabbit_host,
            queue_name,
            routing_key,
    ):
        super().__init__()
        self.logger = logger
        self.gateway_id = gateway_id
        self.rabbit_username = rabbit_username
        self.rabbit_password = rabbit_password
        self.rabbit_host = rabbit_host
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.credentials = pika.PlainCredentials(
            username=self.rabbit_username, password=self.rabbit_password
        )
        self.should_run = True  # Flag to indicate whether the thread should continue running

        self.logger.debug("initialize - Message logger connector")

    def run(self):
        self.logger.debug(f" start monitoring gateway id =: {self.gateway_id}")
        try:
            req = init_get_streaming(self.gateway_id)
            with urllib.request.urlopen(req) as f:
                while (
                        self.should_run
                ):  # Check the flag to see if the thread should continue running
                    msg = f.readline().decode("utf-8")
                    self.logger.debug(f"rx_data{msg}")
                    self.send_data(msg)
                    time.sleep(1)

        except Exception as e:
            self.logger.error(f"ERROR gateway id =: {self.gateway_id} >>>>>>>>>>>>>> {str(e)}")

    def send_data(self, json_data):
        # set [rabbit] configuration
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.rabbit_host, credentials=self.credentials)
        )
        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=self.routing_key,
            body=json.dumps(json_data),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        self.logger.debug(" rx_data sent to the queue")
        connection.close()

    def stop(self):
        self.should_run = False


class StreamEventLogger(object):
    def __init__(
            self,
            logger,
            rabbit_username,
            rabbit_password,
            rabbit_host,
            control_gateways_queue,
            rabbit_message_queue_name,
            rabbit_message_routing_key,
            db_engine,
    ):
        self.logger = logger
        self.rabbit_username = rabbit_username
        self.rabbit_password = rabbit_password
        self.rabbit_host = rabbit_host
        self.control_gateways_queue = control_gateways_queue
        self.rabbit_message_queue_name = rabbit_message_queue_name
        self.rabbit_message_routing_key = rabbit_message_routing_key

        self.credentials = pika.PlainCredentials(
            username=self.rabbit_username, password=self.rabbit_password
        )
        self.engine = db_engine
        self.all_monitored_gws = []
        self.logger.debug("initialize - MetadataLoggerService")

    def call(self, data):
        try:
            data_json = json.loads(data)
            gateway_id = data_json["id"]
            command = data_json["command"]
            if not gateway_id or not command:
                self.logger.error(f"Invalid data received: {data}")
                return

            if command == "start":
                self.start_monitor_gw(gateway_id, self.engine)
            elif command == "stop":
                self.stop_monitor_gw(gateway_id, self.engine)
            else:
                self.logger.error(f"Invalid command received: {command}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error in call: {data}")

    def start_monitor_gw(self, gateway_id: str, db_engine):
        with Session(db_engine) as session:
            gateway_exists = self.check_if_gateway_exists(gateway_id)
            if not gateway_exists:
                monitoredGateway = MonitoredGateways(gateway_id_tti=gateway_id)
                session.add(monitoredGateway)
                session.commit()

                gw_monitored_thread = MessageSubscriptor(
                    self.logger,
                    gateway_id,
                    self.rabbit_username,
                    self.rabbit_password,
                    self.rabbit_host,
                    self.rabbit_message_queue_name,
                    self.rabbit_message_routing_key,
                )
                gw_monitored_thread.start()
                self.all_monitored_gws.append(gw_monitored_thread)
                self.logger.debug("start_monitor gateway added Done!")
            else:
                self.logger.debug(f"start_monitor_gw = {gateway_id} exists!")

    def check_if_gateway_exists(self, gateway_id):
        try:
            with Session(self.engine) as session:
                return session.exec(
                    select(MonitoredGateways).where(MonitoredGateways.gateway_id_tti == gateway_id)
                ).first()
        except Exception as e:
            self.logger.error(f"Error check_if_gateway_exists: {str(e)}")
            raise DatabaseError("check_if_gateway_exists ",
                                f"Error check_if_gateway_exists: {str(e)}")
        finally:
            session.close()

    def stop_monitor_gw(self, gateway_id: str, db_engine):
        self.logger.debug("stop_monitor_gw")
        with Session(db_engine) as session:
            monitored_gateway = self.check_if_gateway_exists(gateway_id)
            if not monitored_gateway:
                self.logger.error(f"No monitored gateway with id {gateway_id} found in the database")
            else:
                session.delete(monitored_gateway)
                session.commit()

                for i, gw_monitored_thread in enumerate(self.all_monitored_gws):
                    if gw_monitored_thread.gateway_id == gateway_id:
                        gw_monitored_thread.stop()  # Stop the thread
                        self.all_monitored_gws.pop(i)  # Remove the thread from the list
                        break

    def get_all_monitor_gateways(self):
        try:
            self.logger.debug(f"get_all_monitore_gateways")
            with Session(self.engine) as session:
                return session.exec(select(MonitoredGateways)).all()

        except Exception as e:
            self.logger.error(f"Error get_all_monitor_gateways: {str(e)}")
            raise DatabaseError("get_all_monitor_gateways ",
                                f"Error check_if_gateway_exists: {str(e)}")
        finally:
            session.close()

    def init_start_monitoring(self):
        try:
            gateways_ids = self.get_all_monitor_gateways()
            self.logger.debug(f"init_start_monitoring")
            for gw in gateways_ids:
                gw_monitored_thread = MessageSubscriptor(
                    self.logger,
                    gw.gateway_id_tti,
                    self.rabbit_username,
                    self.rabbit_password,
                    self.rabbit_host,
                    self.rabbit_message_queue_name,
                    self.rabbit_message_routing_key,
                )
                gw_monitored_thread.start()
                self.all_monitored_gws.append(gw_monitored_thread)
        except Exception as e:
            self.logger.error(f"Error init_start_monitoring: {repr(e)}")

    def callback(self, ch, method, properties, body):
        try:
            self.logger.debug("start callback ")
            t = threading.Thread(target=self.call, args=(json.loads(body.decode("utf-8")),))
            t.start()
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            self.logger.error(f"Error in callback function: {repr(e)}")

    def start_rabbit(self) -> None:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.rabbit_host, credentials=self.credentials)
            )
            channel = connection.channel()
            channel.queue_declare(queue=self.control_gateways_queue, durable=True)
            channel.basic_qos(prefetch_count=1)
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise RabbitMQConnectionError("Failed to connect to RabbitMQ.") from e

        try:
            while True:
                channel.basic_consume(
                    queue=self.control_gateways_queue, on_message_callback=self.callback
                )
                channel.start_consuming()
        except Exception as e:
            self.logger.error(f"RabbitMQ channel was closed: {repr(e)}")
            raise RabbitMQConsumingError(f"Error RabbitMQ consumer: {repr(e)}") from e
