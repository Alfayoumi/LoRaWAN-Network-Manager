#!/bin/bash

ENV APP_DIR /opt/code/tti_message_logger
cd $APP_DIR && pytest -c ./pytest.ini

echo "Tests completed in $APP_DIR"