import json
import os
from typing import List

import pika
from sqlmodel import Session

from dependencies import utility_functions
from dependencies.config import logger_config
from dependencies.exceptions import QueueSendError, EntityNotFound
from schemas.help_schemas import ControlCommands
from schemas.help_schemas import MonitorInfo
from services.utility_services import get_all_network_gateway, get_gateways_for_application, \
    get_gateway_from_db_by_tti_id, get_network_from_db, get_all_gateways_from_db, get_application_from_db, \
    get_all_application_from_db

logger = utility_functions.get_logger(logger_config)
rabbit_username = os.getenv("RABBITMQ_USERNAME")
rabbit_password = os.getenv("RABBITMQ_PASSWORD")
rabbit_host = os.getenv("RABBITMQ_HOST")
credentials = pika.PlainCredentials(username=rabbit_username, password=rabbit_password)


def send_data_to_queue(json_data, rabbit_host, queue_name):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbit_host, credentials=credentials)
        )
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(json_data),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        connection.close()
    except Exception as e:
        logger.error(f" Error in  send_data_to_queue {str(e)}")
        raise QueueSendError(f"Error in  send_data_to_queue {str(e)}")


def send_data(task_data, queue_name):
    try:
        payload = task_data.json()

        if queue_name == "-":
            return "Wrong task type"

        send_data_to_queue(
            json_data=payload,
            rabbit_host=rabbit_host,
            queue_name=queue_name,
        )

        return "Task completed"
    except QueueSendError:
        raise
    except Exception as e:
        logger.error(f"Error in  send_data  {str(e)}")
        raise QueueSendError(f"Error in  send_data {str(e)}")


def start_monitor_gateway(gateway_id: str, db: Session):
    """
    Start monitoring the specified gateway.
    """

    db_gateway = get_gateway_from_db_by_tti_id(gateway_id, db)
    if not db_gateway:
        raise EntityNotFound(entity_name="gateway", entity_id=gateway_id)

    task_data = MonitorInfo(id=gateway_id, command=ControlCommands.START)
    queue_name = os.getenv("CONTROL_GATEWAYS_QUEUE", "control_gateways_queue")
    task_status = send_data(task_data, queue_name)
    return {"task_status": task_status}


def stop_monitor_gateway(gateway_id: str, db: Session):
    """
    Stop monitoring the specified gateway.
    """
    db_gateway = get_gateway_from_db_by_tti_id(gateway_id, db)
    if not db_gateway:
        raise EntityNotFound(entity_name="gateway", entity_id=gateway_id)

    task_data = MonitorInfo(id=gateway_id, command=ControlCommands.STOP)
    queue_name = os.getenv("CONTROL_GATEWAYS_QUEUE", "control_gateways_queue")
    task_status = send_data(task_data, queue_name)
    return {"task_status": task_status}


def stop_monitor_network(network_id: str, db: Session):
    """
    Stop monitoring the specified network.
    """
    db_network = get_network_from_db(network_id, db)
    if not db_network:
        raise EntityNotFound(entity_name="network", entity_id=network_id)

    all_gateways = get_all_network_gateway(network_id, db)
    queue_name = os.getenv("CONTROL_GATEWAYS_QUEUE", "control_gateways_queue")
    task_status = []
    task_data = MonitorInfo(id="", command=ControlCommands.STOP)
    for gateway in all_gateways:
        task_data.id = gateway.gateway_tti_id
        task_status.append(send_data(task_data, queue_name))

    return {"task_status": "\n".join(task_status)}


def start_monitor_network(network_id: str, db: Session):
    """
    Start monitoring the specified network.
    """
    db_network = get_network_from_db(network_id, db)
    if not db_network:
        raise EntityNotFound(entity_name="network", entity_id=network_id)

    all_gateways = get_all_network_gateway(network_id, db)
    queue_name = os.getenv("CONTROL_GATEWAYS_QUEUE", "control_gateways_queue")
    task_status = []
    task_data = MonitorInfo(id="", command=ControlCommands.START)
    for gateway in all_gateways:
        task_data.id = gateway.gateway_tti_id
        task_status.append(send_data(task_data, queue_name))

    return {"task_status": "\n".join(task_status)}


def stop_monitor_all_gateway(db: Session):
    all_gateways = get_all_gateways_from_db(db)
    if not all_gateways:
        raise EntityNotFound(entity_name="gateway", entity_id="No gateways found")

    queue_name = os.getenv("CONTROL_GATEWAYS_QUEUE", "control_gateways_queue")
    task_status = []
    task_data = MonitorInfo(id="", command=ControlCommands.STOP)
    for gateway in all_gateways:
        task_data.id = gateway.gateway_tti_id
        task_status.append(send_data(task_data, queue_name))

    return {"task_status": "\n".join(task_status)}


def start_monitor_all_gateway(db: Session):
    all_gateways = get_all_gateways_from_db(db)
    if not all_gateways:
        raise EntityNotFound(entity_name="gateway", entity_id="No gateways found")

    queue_name = os.getenv("CONTROL_GATEWAYS_QUEUE", "control_gateways_queue")
    task_status = []
    task_data = MonitorInfo(id="", command=ControlCommands.START)
    for gateway in all_gateways:
        task_data.id = gateway.gateway_tti_id
        task_status.append(send_data(task_data, queue_name))

    return {"task_status": "\n".join(task_status)}


def start_monitor_application(application_id: str, db: Session):
    logger.debug("start_monitor_application")
    db_application = get_application_from_db(application_id, db)
    if not db_application:
        raise EntityNotFound(entity_name="application", entity_id=application_id)

    queue_name = os.getenv("CONTROL_APPLICATION_QUEUE", "control_application_queue")
    task_data = MonitorInfo(id=application_id, command=ControlCommands.START)
    task_status = send_data(task_data, queue_name)
    return {"task_status": task_status}


def stop_monitor_application(application_id: str, db: Session):
    logger.debug("stop_monitor_application")
    db_application = get_application_from_db(application_id, db)
    if not db_application:
        raise EntityNotFound(entity_name="application", entity_id=application_id)

    queue_name = os.getenv("CONTROL_APPLICATION_QUEUE", "control_application_queue")
    task_data = MonitorInfo(id=application_id, command=ControlCommands.STOP)
    task_status = send_data(task_data, queue_name)
    return {"task_status": task_status}


def start_monitor_all_application(db: Session):
    all_applications = get_all_application_from_db(db)
    if not all_applications:
        raise EntityNotFound(entity_name="application", entity_id="No application found")

    queue_name = os.getenv("CONTROL_APPLICATION_QUEUE")
    task_status = []
    task_data = MonitorInfo(id="", command=ControlCommands.START)
    logger.debug(f"all_applications  {all_applications}")
    for application in all_applications:
        task_data.id = application.application_id
        task_status.append(send_data(task_data, queue_name))

    return {"task_status": "\n".join(task_status)}


def stop_monitor_all_application(db: Session):
    all_applications = get_all_application_from_db(db)
    if not all_applications:
        raise EntityNotFound(entity_name="application", entity_id="No application found")

    queue_name = os.getenv("CONTROL_APPLICATION_QUEUE", "control_application_queue")
    task_status = []
    task_data = MonitorInfo(id="", command=ControlCommands.STOP)
    for application in all_applications:
        task_data.id = application.application_id
        task_status.append(send_data(task_data, queue_name))

    return {"task_status": "\n".join(task_status)}


def stop_monitor_gateways_of_application(application_id: str, db: Session):
    logger.debug("stop_monitor_gateways_of_application")
    db_application = get_application_from_db(application_id, db)
    if not db_application:
        raise EntityNotFound(entity_name="application", entity_id=application_id)
    task_status = []
    application_queue_name = os.getenv("CONTROL_APPLICATION_QUEUE", "control_application_queue")
    task_status.append(send_data(
        MonitorInfo(id=application_id, command=ControlCommands.STOP), application_queue_name
    ))

    application_gateways_ids = get_gateways_for_application(application_id)
    gw_queue_name = os.getenv("CONTROL_GATEWAYS_QUEUE", "control_gateways_queue")

    gw_task_data = MonitorInfo(id="", command=ControlCommands.STOP)
    for gateway_id in application_gateways_ids:
        gw_task_data.id = gateway_id
        task_status.append(send_data(gw_task_data, gw_queue_name))
    return {"task_status": "\n".join(task_status)}


def start_monitor_gateways_of_application(application_id: str, db: Session):
    logger.debug("start_monitor_gateways_of_application")
    db_application = get_application_from_db(application_id, db)
    if not db_application:
        raise EntityNotFound(entity_name="application", entity_id=application_id)

    task_status = []
    application_queue_name = os.getenv("CONTROL_APPLICATION_QUEUE", "control_application_queue")
    task_status.append(send_data(
        MonitorInfo(id=application_id, command=ControlCommands.START), application_queue_name
    ))

    application_gateways_ids = get_gateways_for_application(application_id)
    gw_queue_name = os.getenv("CONTROL_GATEWAYS_QUEUE", "control_gateways_queue")
    gw_task_data = MonitorInfo(id="", command=ControlCommands.START)
    for gateway_id in application_gateways_ids:
        gw_task_data.id = gateway_id
        task_status.append(send_data(gw_task_data, gw_queue_name))
    return {"task_status": "\n".join(task_status)}


def stop_monitor_gateways_of_all_applications(application_ids: List[str], db):
    logger.debug("stop_monitor_gateways_of_all_applications")
    task_status = []
    for application_id in application_ids:
        db_application = get_application_from_db(application_id, db)
        if not db_application:
            raise EntityNotFound(entity_name="application", entity_id=application_id)

        application_queue_name = os.getenv("CONTROL_APPLICATION_QUEUE", "control_application_queue")
        task_status.append(send_data(
            MonitorInfo(id=application_id, command=ControlCommands.STOP), application_queue_name
        ))
        application_gateways_ids = get_gateways_for_application(application_id)
        gw_queue_name = os.getenv("CONTROL_GATEWAYS_QUEUE", "control_gateways_queue")

        gw_task_data = MonitorInfo(id="", command=ControlCommands.STOP)
        for gateway_id in application_gateways_ids:
            gw_task_data.id = gateway_id
            task_status.append(send_data(gw_task_data, gw_queue_name))

    return {"task_status": "\n".join(task_status)}


def start_monitor_gateways_of_all_applications(application_ids: List[str], db):
    logger.debug("stop_monitor_gateways_of_all_applications")
    task_status = []
    for application_id in application_ids:
        db_application = get_application_from_db(application_id, db)
        if not db_application:
            raise EntityNotFound(entity_name="application", entity_id=application_id)

        application_queue_name = os.getenv("CONTROL_APPLICATION_QUEUE", "control_application_queue")
        task_status.append(send_data(
            MonitorInfo(id=application_id, command=ControlCommands.START), application_queue_name
        ))

        application_gateways_ids = get_gateways_for_application(application_id)
        gw_queue_name = os.getenv("CONTROL_GATEWAYS_QUEUE", "control_gateways_queue")
        gw_task_data = MonitorInfo(id="", command=ControlCommands.START)
        for gateway_id in application_gateways_ids:
            gw_task_data.id = gateway_id
            task_status.append(send_data(gw_task_data, gw_queue_name))

    return {"task_status": "\n".join(task_status)}
