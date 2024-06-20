#!/bin/bash

# Directories to run tests
directories=(
#    "apicelery/scripts"
#     "backend/scripts"
#    "stream_event_logger/scripts"
     "tti_message_logger/scripts"
#    "stream_event_consumer/scripts"
#    "tti_message_consumer/scripts"
#    "kpi_calculation/scripts"
)

# Iterate over directories and run tests
for directory in "${directories[@]}"; do
    echo "Running tests in $directory"
    (cd "$directory" && ./run_tests_local.sh)
    echo "Tests completed in $directory"
    echo ""
done

echo "All tests completed"
