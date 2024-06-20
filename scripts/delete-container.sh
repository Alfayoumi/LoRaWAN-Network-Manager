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

# Parse command-line arguments
CONTAINER_NAME=""
DELETE_IMAGE=false

while [[ $# -gt 0 ]]
do
  case $1 in
    -c|--container)
      shift
      CONTAINER_NAME="$1"
      ;;
    -d|--delete-image)
      DELETE_IMAGE=true
      ;;
    *)
      # Unknown option
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
  shift
done

# Check if container name is provided
if [[ -z "$CONTAINER_NAME" ]]; then
    echo "Container name not specified. Please provide the container name using the -c or --container option."
    exit 1
fi

# Stop and delete the container
docker stop "$CONTAINER_NAME" >/dev/null 2>&1

# Delete the image if requested
if $DELETE_IMAGE; then
    image_name=$(docker inspect --format='{{.Image}}' "$CONTAINER_NAME")
    delete_container "$CONTAINER_NAME"
    delete_image "$image_name"
fi

### note on how to use it
## ./delete-container.sh -c my_container -d