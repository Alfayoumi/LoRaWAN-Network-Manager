# TTI Message Logger Microservice

The TTI Message Logger Microservice is responsible for logging TTI (The Things Industries) 
messages to the specified queue. It connects to the MQTT broker provided 
by TTI, receives sensor data messages, and logs them for further analysis and integration. 
This microservice plays a crucial role in capturing and storing TTI messages for monitoring,
analysis, and auditing purposes.

## Configuration

To configure the TTI Message Logger Microservice, update the following variables in the `ENV/tti_message_logger.env` file:

- **MQTT_USER_TAIL**: The user tail for connecting to the TTI MQTT broker.
- **MQTT_PASS_TTI**: The password for connecting to the TTI MQTT broker.
- **MQTT_HOST**: The hostname or IP address of the TTI MQTT broker.
- **MQTT_PORT**: The port number on which the TTI MQTT broker is listening.
- **MQTT_SENSOR_DATA_SUB_TOPIC**: The MQTT sub-topic for receiving sensor data messages.

- **RABBITMQ_USERNAME**: The username for RabbitMQ authentication.
- **RABBITMQ_PASSWORD**: The password for RabbitMQ authentication.
- **RABBITMQ_HOST**: The hostname or IP address of the RabbitMQ server.
- **RABBITMQ_PORT**: The port number on which RabbitMQ is listening.
- **ROUTING_KEY**: The routing key used for publishing TTI messages to the RabbitMQ exchange.
- **QUEUE_NAME**: The name of the queue where TTI messages will be stored.
- **CONTROL_APPLICATION_QUEUE**: The name of the queue for controlling the application.
- **POSTGRES_URL**: The URL for connecting to the PostgreSQL database.
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
2. Navigate to the `tti_message_logger` directory.
3. Run the following command to execute the tests using Docker:

```bash
./scripts/run_tests_docker.sh
```


### Running Tests Locally

1. Navigate to the `tti_message_logger` directory.
2. Run the following command to install the required dependencies for testing:
    ```bash
      pip install -r requirements/test.txt
    ```
3. Once the dependencies are installed, run the following command to execute the tests locally:

```bash
./scripts/run_tests_local.sh
```