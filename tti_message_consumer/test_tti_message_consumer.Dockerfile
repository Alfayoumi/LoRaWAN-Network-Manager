FROM python:3.9.5-slim-buster

ENV PROJECT_DIR /opt/code
ENV HOME /root
ENV APP_DIR $PROJECT_DIR/tti_message_consumer

# Set a directory for the app
WORKDIR $PROJECT_DIR

# Copy requirements file
COPY requirements/tests.txt $PROJECT_DIR/requirements.txt

# Install pip requirements
RUN pip install --no-cache-dir -r $PROJECT_DIR/requirements.txt

# Copy project source code
COPY . $APP_DIR

# Create reports directory
RUN mkdir -p $PROJECT_DIR/reports

# Set PYTHONPATH environment variable
ENV PYTHONPATH "${PYTHONPATH}:${PROJECT_DIR}"

# Set working directory
WORKDIR $APP_DIR

# Grant execute permission to the test script
RUN chmod +x ./scripts/run_tests_docker.sh

# Run the start script
CMD ["./scripts/run_tests_docker.sh"]
