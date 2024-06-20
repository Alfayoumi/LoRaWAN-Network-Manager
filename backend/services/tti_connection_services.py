from fastapi import Depends
from sqlmodel import Session

from database.db import get_session
from dependencies import utility_functions
from dependencies.config import logger_config
from dependencies.exceptions import RequestError, DatabaseError, TTIException, EntityAlreadyExists
from models.models import ApplicationBase
from schemas.schemas import GatewayCreate
from schemas.schemas import NodeCreate
from .application_services import ApplicationService
from .gateway_services import create_gateway
from .node_services import create_node
from .utility_services import TTI_AUTH
from .utility_services import TTI_BASE_URL
from .utility_services import get_node_device_addr
from .utility_services import make_get_tti_request

logger = utility_functions.get_logger(logger_config)


def get_all_registered_tti_gateways(db: Session) -> str:
    logger.debug("get_all_registered_tti_gateways")
    req_url = f"{TTI_BASE_URL}gateways"

    try:
        all_tti_gateways = make_get_tti_request(req_url, TTI_AUTH)["gateways"]
    except Exception as e:
        logger.exception(f"Failed to get TTI gateways in the function get_all_registered_tti_gateways: {str(e)}")
        return f"Failed to get TTI gateways due to an error: {str(e)}"

    response_error_info = []
    for gateway in all_tti_gateways:
        try:
            gateway_model = GatewayCreate(
                gateway_tti_id=gateway["ids"].get("gateway_id"),
                gateway_eui=gateway["ids"].get("eui"),
                created_at=gateway.get("created_at"),
                updated_at=gateway.get("updated_at"),
                gateway_tb_id="None",
                name=None,
                description=None,
                frequency_plan=None,
                location=None,
                network_id=None,
            )

            create_gateway(db, gateway_model)

        except Exception as e:
            logger.debug(f"{repr(e)}")
            response_error_info.append(f"{repr(e)}")

    if response_error_info:
        error_message = '\n'.join(response_error_info)
        return f"Get All Registered TTI Gateways Task completed with errors:\n{error_message}"
    else:
        return "Get All Registered TTI Gateways Task completed successfully."


def get_all_registered_tti_end_devices_given_application_id(db: Session, application_id):
    logger.debug("get_all_registered_tti_end_devices_given_application_id")
    req_url = f"{TTI_BASE_URL}applications/{application_id}/devices"
    response_error_info = []
    try:
        response_data = make_get_tti_request(req_url, TTI_AUTH)
        all_end_devices = response_data.get("end_devices", [])
    except Exception as e:
        logger.debug(f"Failed to get TTI get_all_registered_tti_end_devices_given_application_id: {str(e)}")
        return f"Failed to get_all_registered_tti_end_devices_given_application_id due to an error: {str(e)}"

    for end_device in all_end_devices:
        node_dev_id = end_device["ids"].get("device_id")
        if not node_dev_id:
            continue
        try:
            node_dev_addr = get_node_device_addr(application_id, node_dev_id)

            end_device_model = NodeCreate(
                node_dev_id=node_dev_id,
                node_dev_addr=node_dev_addr,
                created_at=end_device.get("created_at"),
                updated_at=end_device.get("updated_at"),
                node_eui=end_device["ids"].get("dev_eui"),
                join_eui=end_device["ids"].get("join_eui"),
                application_id=application_id,
            )
            create_node(db, end_device_model)

        except (ValueError, RequestError, TTIException) as e:
            logger.error(f"Failed to get TTI get_node_device_addr: {str(e)}")
            response_error_info.append(f"Failed to get TTI get_node_device_addr = {node_dev_id}")

        except EntityAlreadyExists as e:
            logger.error(f" get_all_registered_tti_end_devices_given_application_id : {str(e)}")
            response_error_info.append(f" application_id = {node_dev_id} AlreadyExists")

        except DatabaseError as e:
            logger.error(f"DatabaseError In function get_all_registered_tti_end_devices_given_application_id: {str(e)}")
            response_error_info.append(f"DatabaseError while adding node_dev_id   = {node_dev_id}")
        except Exception as e:
            logger.debug(f"{repr(e)}")
            response_error_info.append(f"{repr(e)}")

    if response_error_info:
        error_message = "\n".join(response_error_info)
        return f"Get All Registered TTI End Devices Given Application Id Task completed with errors:\n{error_message}"
    else:
        return "Get All Registered TTI End Devices Given Application Id Task completed successfully."


def get_all_registered_tti_application(db: Session):
    req_url = f"{TTI_BASE_URL}applications"
    try:
        all_tti_applications = make_get_tti_request(req_url, TTI_AUTH)["applications"]
    except Exception as e:
        logger.debug(f"Failed to get_all_registered_tti_application: {str(e)}")
        return f"Failed to get_all_registered_tti_application due to an error: {str(e)}"

    response_error_info = []
    for application in all_tti_applications:
        new_application = ApplicationBase(
            application_id=application["ids"].get("application_id"),
            created_at=application["created_at"],
            updated_at=application["updated_at"],
        )
        response_error_info.append(get_all_registered_tti_end_devices_given_application_id(db,
                                                                                           new_application.application_id))
        try:
            ApplicationService.create_application(db, new_application)
        except Exception as e:
            logger.debug(f"{repr(e)}")
            response_error_info.append(f"{repr(e)}")

    if response_error_info:
        error_message = "\n".join(response_error_info)
        return f"Get All Registered TTI Application Task completed with errors:\n{error_message}"
    else:
        return "Get All Registered TTI Application Task completed successfully."


def registered_tti_application(db: Session, application_id):
    req_url = f"{TTI_BASE_URL}applications"
    try:
        all_tti_applications = make_get_tti_request(req_url, TTI_AUTH)["applications"]
    except Exception as e:
        logger.debug(f"Failed to get TTI applications: {str(e)}")
        return f"Failed to get registered_tti_application due to an error: {str(e)}"
    response_error_info = []
    for application in all_tti_applications:
        if application["ids"].get("application_id") == application_id:
            try:
                new_application = ApplicationBase(
                    application_id=application["ids"].get("application_id"),
                    created_at=application["created_at"],
                    updated_at=application["updated_at"],
                )
                get_all_registered_tti_end_devices_given_application_id(
                    db, new_application.application_id
                )
                ApplicationService.create_application(db, new_application)
            except Exception as e:
                logger.debug(f"{repr(e)}")
                response_error_info.append(f"{repr(e)}")
    if response_error_info:
        error_message = "\n".join(response_error_info)
        return f"Get Registered TTI Application Task completed with errors:\n{error_message}"
    else:
        return "Get Registered TTI Application Task completed successfully."


def get_all_registered_tti_resources(db=Depends(get_session)):
    response_error_info = [get_all_registered_tti_gateways(db), get_all_registered_tti_application(db)]
    if response_error_info:
        error_message = "\n".join(response_error_info)
        return f"Get All Registered TTI Resources Task completed with errors:\n{error_message}"
    else:
        return "Get All Registered TTI Resources Task completed successfully."
