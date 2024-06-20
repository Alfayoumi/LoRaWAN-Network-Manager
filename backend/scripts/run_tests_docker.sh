#!/bin/bash

ENV APP_DIR /opt/code/backend
cd $APP_DIR && pytest -c ./pytest.ini

echo "Tests completed in $APP_DIR"