#!/bin/bash

ENV APP_DIR /opt/code/apicelery
cd $APP_DIR && pytest -c ./pytest.ini

echo "Tests completed in $APP_DIR"