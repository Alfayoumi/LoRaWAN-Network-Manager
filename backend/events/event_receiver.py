import json
import pika


class EventReceiver(object):
    def __init__(self, username, password, host, port, queue_name, service, logger):
        self.service_worker = service
        self.queue_name = queue_name
        self.logger = logger

        credentials = pika.PlainCredentials(username, password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, port=port, credentials=credentials)
        )

        channel = connection.channel()
        channel.queue_declare(queue=queue_name)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue_name, on_message_callback=self.on_request)

        self.logger.debug(f"__init__ EventReceiver, queue_name = {queue_name}")
        channel.start_consuming()

    def on_request(self, ch, method, props, body):
        self.logger.debug(f"on_request EventReceiver")
        service_instance = self.service_worker()

        response = None
        try:
            response = service_instance.call(body)
        except Exception as e:
            self.logger.error(f"Error calling service: {str(e)}")

        if response is None:
            response = {
                "error": "Receiver exception",
                "queue": self.queue_name,
                "correlation_id": props.correlation_id,
            }

        result = json.dumps(response)
        ch.basic_publish(
            exchange="",
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=result,
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
