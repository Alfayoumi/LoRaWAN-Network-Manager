import time

import pika
import uuid
import json

timeout = 9000


class NoSubscriberAvailableError(Exception):
    def __init__(self, message="No subscriber available"):
        super().__init__(message)


class EventProducer(object):
    def __init__(self, username, password, host, port, logger):
        self.corr_id = None
        self.response = None
        self.logger = logger
        self.credentials = pika.PlainCredentials(username, password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port, credentials=self.credentials)
        )
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True
        )
        self.logger.debug(f"__init__ EventProducer")

    def on_response(self, ch, method, props, body):
        self.logger.debug(f"on_response EventProducer")
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, queue_name, payload):
        self.logger.debug(f"call EventProducer")
        self.response = None
        self.corr_id = str(uuid.uuid4())

        try:
            queue_state = self.channel.queue_declare(queue_name, passive=True, durable=True)
            if queue_state.method.consumer_count == 0:
                self.logger.debug(f"call Exception No subscriber available ")
                raise NoSubscriberAvailableError()
        except Exception as e:
            self.logger.error(f"Error checking for subscribers: {str(e)}")
            raise NoSubscriberAvailableError()

        self.channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue, correlation_id=self.corr_id
            ),
            body=payload,
        )

        start_time = time.time()
        while self.response is None:
            self.connection.process_data_events()
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                self.logger.error("Timeout waiting for response")
                response = {"error": "Timeout waiting for response"}
                result = json.dumps(response)
                return result

        return self.response
