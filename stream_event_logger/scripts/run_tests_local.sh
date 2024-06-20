#!/bin/bash

set -a
CURRENT_DIR=$(dirname "$(realpath "$0")")
PARENT_DIR=$(dirname "$CURRENT_DIR")
PYTHONPATH="$PARENT_DIR:$CURRENT_DIR:."
set +a

cd "$PARENT_DIR"  # Change the working directory to the root directory

mkdir -p ./reports
pytest -c ./pytest.ini
