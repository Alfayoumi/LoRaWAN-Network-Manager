# TTI Message Consumer Microservice

The TTI Message Consumer Microservice is responsible for consuming and processing TTI (The Things Industries) 
messages in the LoRaWAN Network management system. It connects to the RabbitMQ message broker, 
receives TTI messages from the specified queue, and performs necessary actions based on the received messages. 
This microservice plays a crucial role in processing and handling TTI messages for further analysis and integration 
with other components of the network management system.

## Configuration

To configure the TTI Message Consumer Microservice, update the following variables in the `ENV/tti_message_consumer.env` file:

- **DATABASE_URL**: The URL for connecting to the PostgreSQL database.
- **DB_USER**: The username for the PostgreSQL database.
- **DB_PASSWORD**: The password for the PostgreSQL database.
- **DB_NAME**: The name of the PostgreSQL database.
- **RABBITMQ_HOST**: The hostname or IP address of the RabbitMQ server.
- **RABBITMQ_USERNAME**: The username for RabbitMQ authentication.
- **RABBITMQ_PASSWORD**: The password for RabbitMQ authentication.
- **RABBITMQ_PORT**: The port number on which RabbitMQ is listening.
- **QUEUE_NAME**: The name of the queue from which TTI messages will be consumed.
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
2. Navigate to the `tti_message_consumer` directory.
3. Run the following command to execute the tests using Docker:

```bash
./scripts/run_tests_docker.sh
```


### Running Tests Locally

1. Navigate to the `tti_message_consumer` directory.
2. Run the following command to install the required dependencies for testing:
    ```bash
      pip install -r requirements/test.txt
    ```
3. Once the dependencies are installed, run the following command to execute the tests locally:

```bash
./scripts/run_tests_local.sh
```
