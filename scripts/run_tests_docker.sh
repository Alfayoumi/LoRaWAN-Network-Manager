#!/bin/bash
# set -a not needed as we will execute this in a docker container. Usually is used if the script is executed on local.
# We are in / folder, need to move to the folder containing the source code
cd /opt/code/ && pytest -c ./pytest.ini