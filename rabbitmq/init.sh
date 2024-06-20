#!/usr/bin/env bash

set -e
(
count=0;
# Execute list_users until service is up and running
until timeout 5 rabbitmqctl list_users >/dev/null 2>/dev/null || (( count++ >= 60 )); do sleep 1; done;

# Register user
if rabbitmqctl list_users | grep $RABBITMQ_USERNAME > /dev/null
then
  echo "User '$RABBITMQ_USERNAME' already exist, skipping user creation"
else
  echo "Creating user '$RABBITMQ_USERNAME'..."
  rabbitmqctl add_user $RABBITMQ_USERNAME $RABBITMQ_PASSWORD
  rabbitmqctl set_user_tags $RABBITMQ_USERNAME administrator
  rabbitmqctl set_permissions -p / $RABBITMQ_USERNAME ".*" ".*" ".*"
  echo "User '$RABBITMQ_USERNAME' creation completed"
fi
) &

# Call original entrypoint
exec docker-entrypoint.sh rabbitmq-server $@
