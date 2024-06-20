#!/bin/bash

# Set the list of services to stop
SERVICES=("backend" "api-celery" "stream_event_logger" "tti_message_logger" "stream_event_consumer" "tti_message_consumer" "kpi_calculation" "grafana" "pgadmin" "postgres")

for service in "${SERVICES[@]}"
do
  # stop service
  docker-compose stop "$service"
done

# stop RabbitMQ
docker-compose stop rabbitmq
