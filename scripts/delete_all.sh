#!/bin/bash

# Delete container
delete_container() {
    local container="$1"
    docker rm "$container"
}

# Delete image
delete_image() {
    local image="$1"
    docker rmi "$image"
}

CONTAINERS=("metadata-apicelery" "kpi_calculation" "tti_message_consumer" "stream_event_consumer" "tti_message_logger_service" "stream_event_logger_service" "api-backend" )

# Iterate over services and delete the container and image
for CONTAINER_NAME in "${CONTAINERS[@]}"
do
    # Stop and delete the container
    docker stop "$CONTAINER_NAME" >/dev/null 2>&1
    image_name=$(docker inspect --format='{{.Image}}' "$CONTAINER_NAME")
    delete_container "$CONTAINER_NAME"
    delete_image "$image_name"
done