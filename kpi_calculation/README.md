# KPI Calculation Microservice

The KPI Calculation Microservice is responsible for calculating KPIs
for the LoRaWAN Network management system. It processes data collected from various sources, 
performs calculations, and generates meaningful insights and metrics about the network's 
performance and health.

## Configuration

To configure the KPI Calculation Microservice, update the following variables in the `ENV/kpi-calculation.env` file:

- **LOG_LEVEL**: The log level for the microservice's logger.
- **LOG_FILE**: The path to the log file for storing log messages.
- **MAX_BYTES**: The maximum size of the log file in bytes before rotation.
- **BACKUP_COUNT**: The number of log file backups to keep.
- **LOGGER_NAME**: The name of the logger used by the microservice.
- **POSTGRES_URL**: The URL for connecting to the PostgreSQL database.
- **RABBITMQ_HOST**: The hostname or IP address of the RabbitMQ server.
- **RABBITMQ_PORT**: The port number on which RabbitMQ is listening.
- **RABBITMQ_USERNAME**: The username for RabbitMQ authentication.
- **RABBITMQ_PASSWORD**: The password for RabbitMQ authentication.

Make sure to update these variables with your specific values before running the microservice.

## Running Tests

To run tests for the KPI Calculation Microservice, you have two options: 
running tests using Docker or running tests locally.

### Running Tests with Docker

1. Make sure Docker is installed and running on your machine.
2. Navigate to the `kpi_calculation` directory.
3. Run the following command to execute the tests using Docker:

```bash
./scripts/run_tests_docker.sh
```


### Running Tests Locally

1. Navigate to the `kpi_calculation` directory.
2. Run the following command to install the required dependencies for testing:
    ```bash
      pip install -r requirements/test.txt
    ```
3. Once the dependencies are installed, run the following command to execute the tests locally:

```bash
./scripts/run_tests_local.sh
```