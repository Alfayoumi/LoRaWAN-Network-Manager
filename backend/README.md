# Backend Microservice
The Backend Microservice is responsible for providing the API for the LoRaWAN Network management system. 
It handles various operations such as data retrieval,
processing, and storage. This microservice serves as the backbone of the system, allowing other 
components to interact with the data and perform network management tasks.


## Configuration

To configure the Backend Microservice, update the following variables in the `ENV/api.env` file:

- **CMT_INFRASTRUCTURE_MANAGER_BASE_URL**: The base URL of the Infrastructure Manager API of the CMT.
- **CMT_INFRASTRUCTURE_MANAGER_TAIL_URL**: The tail URL for retrieving infrastructure manager data of the CMT.
- **CMT_INTEGRATION_MANAGER_BASE**: The base URL of the Integration Manager API of the CMT.
- **CMT_INTEGRATION_MANAGER_AUTH_API_KEY**: The API key for authentication with the Integration Manager API of the CMT.
- **TB_BASE_URL**: The base URL of the ThingsBoard API for telemetry retrieval.
- **TB_TAIL_URL**: The tail URL for retrieving telemetry data from ThingsBoard.
- **BASE_TTI_NS_ADDRESS**: The base URL of the LoRaWAN Network Server's application namespace.
- **TTI_BASE_URL**: The base URL of the LoRaWAN Network Server API.
- **TTI_EVENT_URL**: The URL for receiving events from the LoRaWAN Network Server.
- **RABBITMQ_BROKER**: The URL of the RabbitMQ message broker.
- **RABBITMQ_USERNAME**: The username for RabbitMQ authentication.
- **RABBITMQ_PASSWORD**: The password for RabbitMQ authentication.
- **RABBITMQ_HOST**: The hostname or IP address of the RabbitMQ server.
- **QUEUE_NAME**: The name of the queue where of the stream_event_queue.
- **ROUTING_KEY**: The routing key used for task routing.
- **RABBITMQ_PORT**: The port number on which RabbitMQ is listening.

- **LOG_LEVEL**: The log level for the microservice's logger.
- **LOG_FILE**: The path to the log file for storing log messages.
- **MAX_BYTES**: The maximum size of the log file in bytes before rotation.
- **BACKUP_COUNT**: The number of log file backups to keep.
- **LOGGER_NAME**: The name of the logger used by the microservice.

Make sure to update these variables with your specific values before running the microservice.


## Running Tests

To run tests for the Backend Microservice, you have two options: running tests using Docker or running tests locally.

### Running Tests with Docker

1. Make sure Docker is installed and running on your machine.
2. Navigate to the `backend` directory.
3. Run the following command to execute the tests using Docker:

```bash
./scripts/run_tests_docker.sh
```


### Running Tests Locally

1. Navigate to the `backend` directory.
2. Run the following command to install the required dependencies for testing:
    ```bash
      pip install -r requirements/test.txt
    ```
3. Once the dependencies are installed, run the following command to execute the tests locally:

```bash
./scripts/run_tests_local.sh
```