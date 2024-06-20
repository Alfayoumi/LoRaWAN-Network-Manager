# API Celery Microservice

The API Celery Microservice is a service designed to handle asynchronous requests 
in a distributed environment. It leverages Celery, a powerful distributed task queue
library, to execute tasks asynchronously and improve 
the responsiveness and scalability of the application.

## Configuration

To configure the API Celery Microservice, update the following variables in the `ENV/apicelery.env` file:

- **RABBITMQ_BROKER**: The URL of the RabbitMQ message broker used by Celery.
- **RABBITMQ_USERNAME**: The username for RabbitMQ authentication.
- **RABBITMQ_PASSWORD**: The password for RabbitMQ authentication.
- **RABBITMQ_HOST**: The hostname or IP address of the RabbitMQ server.
- **QUEUE_NAME**: The name of the queue where Celery tasks will be stored.
- **ROUTING_KEY**: The routing key used for task routing.
- **RABBITMQ_PORT**: The port number on which RabbitMQ is listening.
- **LOG_LEVEL**: The log level for the microservice's logger.
- **LOG_FILE**: The path to the log file for storing log messages.
- **MAX_BYTES**: The maximum size of the log file in bytes before rotation.
- **BACKUP_COUNT**: The number of log file backups to keep.
- **LOGGER_NAME**: The name of the logger used by the microservice.

Make sure to update these variables with your specific values before running the microservice.
 
