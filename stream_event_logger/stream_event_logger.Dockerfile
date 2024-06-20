FROM python:3.9.5-slim-buster

ENV PROJECT_DIR /opt/code
ENV HOME /root
RUN mkdir -p $PROJECT_DIR

# set a directory for the app
WORKDIR $PROJECT_DIR

COPY requirements/stream_event_logger.txt $PROJECT_DIR/requirements.txt

# Install pip requirements
RUN pip install -r $PROJECT_DIR/requirements.txt

COPY .  $PROJECT_DIR/stream_event_logger
ENV PYTHONPATH "${PYTHONPATH}:${PROJECT_DIR}/stream_event_logger"