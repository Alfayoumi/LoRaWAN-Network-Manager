#!/bin/bash

# Set the list of services to start
SERVICES=("postgres" "pgadmin" "grafana" "backend" "api-celery" "stream_event_logger" "tti_message_logger" "stream_event_consumer" "tti_message_consumer" "kpi_calculation")

# Parse command-line arguments
PRINT_LOGS=true

while [[ $# -gt 0 ]]
do
  case $1 in
    -n|--no-logs)
      PRINT_LOGS=false
      ;;
    *)
      # Unknown option
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
  shift
done

# Function to start a service
start_service() {
  local service="$1"
  docker-compose up ${PRINT_LOGS:+-d} "$service"
}

# Start RabbitMQ in the background
docker-compose up -d rabbitmq
# Wait until RabbitMQ is up and running
until docker-compose exec rabbitmq rabbitmqctl ping >/dev/null 2>&1; do
  sleep 1
done

# Start each service
for service in "${SERVICES[@]}"
do
  start_service "$service"
done
