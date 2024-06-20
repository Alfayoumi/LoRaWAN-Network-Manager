import json
import os

from dependencies.config import logger_config
from events.event_producer import EventProducer, NoSubscriberAvailableError
from worker import celery_app
from dependencies.utility_functions import get_logger
from celery.utils.log import get_task_logger

logger = get_logger(logger_config)
celery_log = get_task_logger(__name__)


@celery_app.task(name="process_workflow")
def process_workflow(payload, queue_name):
    payload_json = json.loads(payload)
    task_type = payload_json["task_type"]

    event_producer = None

    try:
        event_producer = EventProducer(
            username=os.getenv("RABBITMQ_USERNAME"),
            password=os.getenv("RABBITMQ_PASSWORD"),
            host=os.getenv("RABBITMQ_HOST"),
            port=os.getenv("RABBITMQ_PORT"),
            logger=logger,
        )
    except Exception as e:
        # Handle the exception
        logger.error(f"An error occurred while creating the EventProducer:{str(e)}")
        raise

    try:
        response = event_producer.call(queue_name, payload)
    except NoSubscriberAvailableError as e:
        celery_log.info(task_type + " task failed: " + str(e))
        return {"status": "error", "message": str(e)}

    if not response:
        celery_log.info(task_type + " task failed: no response received")
        return {"status": "error", "message": "No response received"}

    try:
        response_json = json.loads(response)
    except json.JSONDecodeError as e:
        celery_log.error(task_type + " task failed: " + str(e))
        return {"status": "error", "message": "Failed to decode response as JSON"}
    except ValueError:
        celery_log.error(task_type + " task failed: response is not a valid JSON string")
        return {"status": "error", "message": "Failed to parse response as JSON"}
    except Exception as e:
        celery_log.error(task_type + " task failed with an unexpected error: " + str(e))
        return {
            "status": "error",
            "message": "An unexpected error occurred while processing the task",
        }

    celery_log.info(task_type + " task completed")
    return response_json
