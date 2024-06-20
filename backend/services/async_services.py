import json

from sqlmodel import Session

from database.db import db_engine
from dependencies import utility_functions
from dependencies.config import logger_config
from backend.dependencies.exceptions import InvalidFunctionName, InternalServerError
from .tti_connection_services import get_all_registered_tti_application
from .tti_connection_services import get_all_registered_tti_gateways
from .tti_connection_services import get_all_registered_tti_resources

logger = utility_functions.get_logger(logger_config)


def get_session_db() -> Session:
    """
    Return a new database session for interacting with the database.
    """
    # Open a new database session with the engine and return it to the caller
    return Session(db_engine)


class AsyncServices(object):
    def __init__(self):
        pass

    @staticmethod
    def call(body):
        logger.debug(f"call AsyncServices ")
        logger.debug(f"body {body} ")
        body = json.loads(body)
        func_name = body.get("func_name")

        payload = {"result": "TASK_COMPLETED"}
        # Call the corresponding function with the provided data
        with get_session_db() as db:
            try:
                if func_name == "get_all_registered_tti_gateways":
                    logger.debug(f"get_all_registered_tti_gateways")
                    get_all_registered_tti_gateways(db)
                    payload = {"result": "get_all_registered_tti_gateways TASK_COMPLETED"}

                elif func_name == "get_all_registered_tti_application":
                    logger.debug(f"get_all_registered_tti_application")
                    get_all_registered_tti_application(db)
                    payload = {"result": "get_all_registered_tti_application TASK_COMPLETED"}

                elif func_name == "get_all_registered_tti_resources":
                    logger.debug(f"get_all_registered_tti_resources")
                    get_all_registered_tti_resources(db)
                    payload = {"result": "get_all_registered_tti_resources TASK_COMPLETED"}

                else:
                    raise InvalidFunctionName(f"Invalid function name: {func_name}")
            except Exception as e:
                raise InternalServerError(detail=str(e))

        return json.dumps(payload)
