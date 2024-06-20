import json
import re
import threading
import time
import traceback

import paho.mqtt.client as mqtt
import pika
from sqlmodel import Session
from sqlmodel import select

from database.db import MonitoredApplications
from dependencies.exceptions import RabbitMQConnectionError, RabbitMQConsumingError, DatabaseError, \
    TTIMessageLoggerError


class TtiMessageLogger(threading.Thread):
    def __init__(
            self,
            logger,
            application_id,
            rabbit_username,
            rabbit_password,
            rabbit_host,
            queue_name,
            routing_key,
            mqtt_host,
            mqtt_port,
            mqtt_user,
            mqtt_pass,
            mqtt_sensor_data_sub_topic,
    ):
        super().__init__()
        self.logger = logger
        self.application_id = application_id
        self.rabbit_username = rabbit_username
        self.rabbit_password = rabbit_password
        self.rabbit_host = rabbit_host
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.credentials = pika.PlainCredentials(
            username=self.rabbit_username, password=self.rabbit_password
        )
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_user = mqtt_user
        self.mqtt_pass = mqtt_pass
        self.mqtt_sensor_data_sub_topic = mqtt_sensor_data_sub_topic
        self.mqttclient = mqtt.Client()
        self.logger.debug("initialize - Message logger connector")
        self.mqtt_connect()

    def run(self):
        self.logger.debug(f" start monitoring application_id =: {self.application_id}")
        try:
            self.mqttclient.loop_forever()
        except Exception as e:
            self.logger.error(f"ERROR in start monitoring application_id =: {self.application_id} the error = {str(e)}")

    def mqtt_connect(self):
        try:
            self.logger.debug("mqtt_connect start!")
            self.mqttclient = mqtt.Client()
            self.mqttclient.on_message = self.on_message
            self.mqttclient.on_connect = self.on_connect
            self.mqttclient.on_publish = self.on_publish
            self.mqttclient.on_subscribe = self.on_subscribe
            self.mqttclient.on_disconnect = self.on_disconnect
            self.mqttclient.username_pw_set(username=self.mqtt_user, password=self.mqtt_pass)
            # Connect to MQTT broker
            self.mqttclient.connect(self.mqtt_host, int(self.mqtt_port), keepalive=10)
            self.logger.debug("mqtt_connect end!")
        except Exception as e:
            self.logger.error("Error occurred in mqtt_connect:")
            self.logger.error(f" the error = {str(e)}")
            self.logger.error(traceback.format_exc())
            raise

    def mqtt_reconnect(self):
        self.logger.debug(f"mqtt_reconnect")
        self.logger.debug("[MQTT] Reconnecting...")
        time.sleep(3)
        self.mqtt_connect()

    def on_connect(self, mqttc, obj, flags, rc):
        self.logger.debug(f"on_connect")
        if rc == 0:
            # Subscribe to topics
            self.logger.debug(f"[MQTT] Subscribing to topic:  {self.mqtt_sensor_data_sub_topic}")
            self.mqttclient.subscribe(self.mqtt_sensor_data_sub_topic, 0)
        else:
            self.logger.debug(f"[MQTT] Bad connection: rc . Will auto-reconnect  {rc}")
            self.mqtt_reconnect()

    def send_data(self, json_data):
        self.logger.debug(f"send_data")
        try:
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
            connection.close()
        except Exception as e:
            self.logger.error(f"Error sending message to RabbitMQ: {e}")

    def on_message(self, mqttc, obj, msg):
        self.logger.debug(f"on_message")
        try:
            topic = re.split("/", msg.topic)[-1]
            json_msg = json.loads(msg.payload)
            if topic in ["up", "join"]:
                self.send_data(json_msg)
        except Exception as e:
            self.logger.error(f"ERROR parsing message {str(e)}")
            self.logger.error(traceback.format_exc())

    def on_publish(self, mqttc, obj, mid):
        self.logger.debug(f"on_publish")

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        self.logger.debug(f"on_subscribe")

    def on_disconnect(self, mqttc, userdata, rc):
        self.logger.debug(f"on_disconnect")
        if rc != 0:
            self.logger.debug("[MQTT] Unexpected MQTT disconnection")  # . Will auto-reconnect")
            self.mqtt_reconnect()
        else:
            self.logger.debug("[MQTT] Disconnecting MQTT")

    def stop(self):
        self.logger.debug(f" stop monitoring application_id =: {self.application_id}")
        try:
            self.mqttclient.disconnect()
            self.mqttclient.loop_stop()
        except Exception as e:
            self.logger.error(f"ERROR stop application_id =: {self.application_id}  the error = {str(e)}")


class TtiMessageLoggerService(object):
    def __init__(
            self,
            logger,
            rabbit_username,
            rabbit_password,
            rabbit_host,
            queue_control_command_name,
            rabbit_message_queue_name,
            rabbit_message_routing_key,
            db_engine,
            mqtt_pass,
            mqtt_host,
            mqtt_port,
            mqtt_sensor_data_sub_topic,
            mqtt_user_tail,
    ):
        self.logger = logger
        self.rabbit_username = rabbit_username
        self.rabbit_password = rabbit_password
        self.rabbit_host = rabbit_host
        self.queue_control_command_name = queue_control_command_name
        self.rabbit_message_queue_name = rabbit_message_queue_name
        self.rabbit_message_routing_key = rabbit_message_routing_key
        self.credentials = pika.PlainCredentials(
            username=self.rabbit_username, password=self.rabbit_password
        )
        self.engine = db_engine
        self.mqtt_pass = mqtt_pass
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_sensor_data_sub_topic = mqtt_sensor_data_sub_topic
        self.mqtt_user_tail = mqtt_user_tail
        self.all_monitored_applications = []
        self.logger.debug("initialize - MetadataLoggerService")

    def get_monitored_application(self, application_id):
        try:
            with Session(self.engine) as session:
                return session.exec(
                    select(MonitoredApplications).where(
                        MonitoredApplications.application_id == application_id
                    )
                ).first()
        except Exception as e:
            self.logger.error(f"Error in check_if_application_exists: {str(e)}")
            raise DatabaseError("check_if_application_exists ",
                                f"Error in check_if_application_exists: {str(e)}")

    def add_application_to_monitored_table(self, application_id):
        try:
            with Session(self.engine) as session:
                session.add(MonitoredApplications(application_id=application_id))
                session.commit()
        except Exception as e:
            self.logger.error(f"Error in add_application_to_monitored_table: {str(e)}")
            raise DatabaseError("add_application_to_monitored_table ",
                                f"Error in add_application_to_monitored_table: {str(e)}")

    def delete_application_from_monitored_table(self, application_id):
        try:
            with Session(self.engine) as session:
                monitored_application = session.exec(select(MonitoredApplications).where(
                    MonitoredApplications.application_id == application_id)).first()
                session.delete(monitored_application)
                session.commit()
        except Exception as e:
            self.logger.error(f"Error in delete_application_from_monitored_table: {str(e)}")
            raise DatabaseError("delete_application_from_monitored_table ",
                                f"Error in delete_application_from_monitored_table: {str(e)}")

    def stop_monitor_application(self, application_id: str):
        try:
            self.logger.debug("stop_monitor_application")
            monitored_application = self.get_monitored_application(application_id)
            if not monitored_application:
                self.logger.debug(f"No monitored application with id {application_id} found in the database")
                return
            self.delete_application_from_monitored_table(application_id)

            for i, application_tti_message_logger in enumerate(self.all_monitored_applications):
                if application_tti_message_logger.application_id == application_id:
                    application_tti_message_logger.stop()  # Stop the thread
                    self.all_monitored_applications.pop(i)  # Remove the thread from the list
                    break
        except DatabaseError:
            raise
        except Exception as e:
            self.logger.error(f"Error stop_monitor_application: {str(e)}")
            raise TTIMessageLoggerError(f"Error stop_monitor_application: {str(e)}") from e

    def start_monitor_application(self, application_id: str):
        self.logger.debug("start_monitor_application!")
        try:
            monitored_application = self.get_monitored_application(application_id)
            if not monitored_application:
                self.add_application_to_monitored_table(application_id)

                mqtt_user = f"{application_id}{self.mqtt_user_tail}"
                application_tti_message_logger = TtiMessageLogger(
                    self.logger,
                    application_id,
                    self.rabbit_username,
                    self.rabbit_password,
                    self.rabbit_host,
                    self.rabbit_message_queue_name,
                    self.rabbit_message_routing_key,
                    self.mqtt_host,
                    self.mqtt_port,
                    mqtt_user,
                    self.mqtt_pass,
                    self.mqtt_sensor_data_sub_topic,
                )

                application_tti_message_logger.start()
                self.all_monitored_applications.append(application_tti_message_logger)
                self.logger.debug(f"start_monitor_application = {application_id} added Done!")
            else:
                self.logger.debug(f"  start_monitor_application = {application_id} exists!")
        except DatabaseError:
            raise
        except Exception as e:
            self.logger.error(f"Error start_monitor_application: {str(e)}")
            raise TTIMessageLoggerError(f"Error start_monitor_application: {str(e)}") from e

    def call(self, data):
        try:
            data_json = json.loads(data)
            application_id = data_json.get("id")
            command = data_json.get("command")
            if not application_id or not command:
                self.logger.error(f"Invalid data received: {data}")
                return

            if command == "start":
                self.start_monitor_application(application_id)
            elif command == "stop":
                self.stop_monitor_application(application_id)
            else:
                self.logger.error(f"Invalid command received: {command}")

        except Exception as e:
            self.logger.error(f"{repr(e)}")

    def callback(self, ch, method, properties, body):
        self.logger.debug("start callback ")
        self.call(json.loads(body.decode("utf-8")))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_rabbit(self) -> None:
        try:
            self.logger.debug("start callback ")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.rabbit_host, credentials=self.credentials)
            )
            # Declare the queue
            channel = connection.channel()
            channel.queue_declare(queue=self.queue_control_command_name, durable=True)
            channel.basic_qos(prefetch_count=1)

        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise RabbitMQConnectionError("Failed to connect to RabbitMQ.") from e

        try:
            while True:
                channel.basic_consume(
                    queue=self.queue_control_command_name, on_message_callback=self.callback
                )
                channel.start_consuming()
        except Exception as e:
            self.logger.error(f"RabbitMQ channel was closed in start_rabbit function: {repr(e)}")
            raise RabbitMQConsumingError(f"Error starting RabbitMQ consumer in start_rabbit function: {repr(e)}") from e

    def get_all_monitor_applications_ids(self):
        self.logger.debug(f"get_all_monitor_applications_ids")
        try:
            with Session(self.engine) as session:
                return session.exec(select(MonitoredApplications)).all()
        except Exception as e:
            self.logger.error(f"Error in get_all_monitor_applications_ids: {str(e)}")
            raise DatabaseError("get_all_monitor_applications_ids ",
                                f"Error in get_all_monitor_applications_ids: {str(e)}")

    def init_start_monitoring(self):
        self.logger.debug(f"init_start_monitoring")
        try:
            applications_ids = self.get_all_monitor_applications_ids()
            for application in applications_ids:
                self.start_monitor_application(application.application_id)
        except Exception as e:
            self.logger.error(f"Error in init_start_monitoring: {repr(e)}")
