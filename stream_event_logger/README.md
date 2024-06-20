# Stream Event Logger Microservice

The Stream Event Logger Microservice is responsible for logging stream events from 
the LoRaWAN Network management system. It connects to the TTI gateway server, receives
stream events for a specific gateway, and stores them in a dedicated queue in the RabbitMQ 
message broker. After the Stream Event Logger Microservice stores the stream events in the 
dedicated queue in the RabbitMQ message broker, other microservices can consume these data/events 
messages from the queue.


## Configuration

To configure the Stream Event Logger Microservice, update the following variables in the `ENV/stream_event_logger.env` file:

- **POSTGRES_URL**: The URL for connecting to the PostgreSQL database.
- **DB_USER**: The username for the PostgreSQL database.
- **DB_PASSWORD**: The password for the PostgreSQL database.
- **DB_NAME**: The name of the PostgreSQL database.
- **RABBITMQ_HOST**: The hostname or IP address of the RabbitMQ server.
- **RABBITMQ_USERNAME**: The username for RabbitMQ authentication.
- **RABBITMQ_PASSWORD**: The password for RabbitMQ authentication.
- **RABBITMQ_PORT**: The port number on which RabbitMQ is listening.
- **ROUTING_KEY**: The routing key used for subscribing to stream events.
- **QUEUE_NAME**: The name of the queue from which stream events will be consumed.
- **CONTROL_GATEWAYS_QUEUE**: The name of the queue for controlling gateways.
- **TTI_EVENT_URL**: The URL for receiving events from the LoRaWAN Network Server.
- **LOG_LEVEL**: The log level for the microservice's logger.
- **LOG_FILE**: The path to the log file for storing log messages.
- **MAX_BYTES**: The maximum size of the log file in bytes before rotation.
- **BACKUP_COUNT**: The number of log file backups to keep.
- **LOGGER_NAME**: The name of the logger used by the microservice.

Make sure to update these variables with your specific values before running the microservice.


## Running Tests

To run tests for the KPI Calculation Microservice, you have two options: 
running tests using Docker or running tests locally.

### Running Tests with Docker

1. Make sure Docker is installed and running on your machine.
2. Navigate to the `stream_event_logger` directory.
3. Run the following command to execute the tests using Docker:

```bash
./scripts/run_tests_docker.sh
```


### Running Tests Locally

1. Navigate to the `stream_event_logger` directory.
2. Run the following command to install the required dependencies for testing:
    ```bash
      pip install -r requirements/test.txt
    ```
3. Once the dependencies are installed, run the following command to execute the tests locally:

```bash
./scripts/run_tests_local.sh
```
 
