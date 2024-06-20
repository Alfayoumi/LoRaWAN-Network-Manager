import json
import os
import urllib.request as request
from typing import Optional, List

from sqlmodel import Session
from sqlmodel import col
from sqlmodel import select

from database.db import db_engine
from dependencies import utility_functions
from dependencies.config import logger_config
from dependencies.exceptions import DatabaseError, TTIException, RequestError
from models.models import Cluster, Deployment, AllRelation, Application
from models.models import Gateway
from models.models import Network
from models.models import Node
from schemas.schemas import DeploymentRead

logger = utility_functions.get_logger(logger_config)

# Load environment variables
CMT_INFRASTRUCTURE_MANAGER_BASE_URL = os.getenv("CMT_INFRASTRUCTURE_MANAGER_BASE_URL")
CMT_INFRASTRUCTURE_MANAGER_TAIL_URL = os.getenv("CMT_INFRASTRUCTURE_MANAGER_TAIL_URL")
CMT_INTEGRATION_MANAGER_BASE = os.getenv("CMT_INTEGRATION_MANAGER_BASE")
CMT_INTEGRATION_MANAGER_API_KEY = os.getenv("CMT_INTEGRATION_MANAGER_AUTH_API_KEY")
BASE_TTI_NS_ADDRESS = os.getenv("BASE_TTI_NS_ADDRESS")
TTI_AUTH = os.getenv("TTI_AUTH")
TTI_BASE_URL = os.getenv("TTI_BASE_URL")

TB_BASE_URL = os.getenv("TB_BASE_URL")
TB_TAIL_URL = os.getenv("TB_TAIL_URL")


def make_request(url: str, method: str, headers: dict, body=None):
    """
    Makes an HTTP request and returns the response body as a string.

    Args:
        url (str): The URL to request.
        method (str): The HTTP method to use (e.g. "GET", "POST", etc.).
        headers (dict): A dictionary of headers to include in the request.
        body (str, optional): The body of the request. Defaults to None.

    Returns:
        str: The response body as a string.
    """
    try:
        request_data = request.Request(
            url=url, headers=headers, method=method, data=body.encode() if body else None
        )

        with request.urlopen(request_data) as f:
            return f.readline().decode("utf-8")
    except Exception as e:
        logger.error("An error occurred during the request.", exc_info=True)
        raise RequestError("An error occurred during the request.", original_exception=e)


# URL CONSTRUCTION
def construct_url_things_board(base: str, tail: str, network_id: str) -> str:
    """
    Returns a URL for a given base, tail, and network ID.

    Args:
        base (str): The base URL for the ThingsBoard server.
        tail (str): The tail of the URL.
        network_id (str): The ID of the network.

    Returns:
        str: The full URL.
    """
    variables = {
        'base': base,
        'tail': tail,
        'network_id': network_id
    }

    missing_variables = [var_name for var_name, var_value in variables.items() if var_value is None]
    if missing_variables:
        raise ValueError(f"Invalid arguments: {', '.join(missing_variables)} must be provided.")

    return f"{base}{network_id}{tail}"


def construct_url(
        base: str,
        prefix: str,
        tail: str,
        prefix_id: Optional[str] = None,
        list_type_name: Optional[str] = None,
) -> str:
    """
    Returns a URL for a given base, prefix, prefix ID, list type name, and tail.

    Args:
        base (str): The base URL.
        prefix (str): The prefix of the URL.
        tail (str): The tail of the URL.
        prefix_id (str): The ID of the prefix. If None, the ID will not be included in the URL.
        list_type_name (str): The name of the list type.

    Returns:
        str: The full URL.
    """
    if None in (base, prefix, tail):
        raise ValueError("Invalid arguments: base, prefix, and tail must be provided.")

    return (
        f"{base}{prefix}/{prefix_id}/{list_type_name}{tail}"
        if prefix_id
        else f"{base}{prefix}{tail}"
    )


def construct_device_addr_url(base: str, tti_app_id: str, node_dev_id: str):
    """
    Returns the URL to get the device address for a given TTI application and node device ID.

    Args:
        base (str): The base URL for the TTI namespace server.
        tti_app_id (str): The ID of the TTI application.
        node_dev_id (str): The ID of the node device.

    Returns:
        str: The URL to get the device address.
    """
    variables = {
        'base': base,
        'tti_app_id': tti_app_id,
        'node_dev_id': node_dev_id
    }

    missing_variables = [var_name for var_name, var_value in variables.items() if var_value is None]
    if missing_variables:
        raise ValueError(f"Invalid arguments: {', '.join(missing_variables)} must be provided.")

    url = f"{base}{tti_app_id}/devices/{node_dev_id}"
    return url


def construct_tti_application_id_url(base, network_id):
    """
    Returns the URL to get the TTI application ID for a given network ID.

    Args:
        base (str): The base URL for the CMT integration manager.
        network_id (str): The ID of the network.

    Returns:
        str: The URL to get the TTI application ID.
    """
    if not all((base, network_id)):
        raise ValueError("Invalid arguments: base and network_id must be provided.")

    return f"{base}{network_id}"


# THINGS BOARD REQUESTS
def get_gateway_data_from_things_board(base, tail, device_id, tb_auth):
    logger.debug(f"get_gateway_data_from_things_board")
    """
    Get gateway data from ThingsBoard API.

    Args:
        base_url (str): The base URL of the ThingsBoard API.
        tail_url (str): The tail URL of the API request.
        device_id (str): The ID of the gateway device to get data for.
        auth_token (str): The authorization token to use for the API request.

    Returns:
        dict: A dictionary containing the gateway data.

    Raises:
        ValueError: If the API response cannot be parsed.
        RequestError: If the API request fails.

    """
    try:
        url_tb = construct_url_things_board(base, tail, device_id)
        headers = {"x-authorization": tb_auth, "Content-Type": "application/json"}
        logger.debug(f"url_tb{url_tb}")

        response = make_request(url_tb, "GET", headers=headers)
        logger.debug(f"response{response}")
        gw_data = json.loads(response)
    except ValueError as e:
        raise ValueError(
            f"{str(e)}. Error in fetching gateway data from ThingsBoard API in the function "
            f"get_gateway_data_from_things_board.")
    except RequestError as e:
        raise RequestError(
            f"{str(e)}. Error in fetching gateway data from ThingsBoard API in the function "
            f"get_gateway_data_from_things_board.")
    except Exception as e:
        raise Exception(
            f"Error in fetching gateway data from ThingsBoard API in the function "
            f"get_gateway_data_from_things_board: {e}")

    gateway_tti_id = gw_data.get("technology_spec", {}).get("gwId")
    gateway_eui = gw_data.get("technology_spec", {}).get("gwEUI")
    frequency_plan = gw_data.get("technology_spec", {}).get("frequencyPlan")
    gw_name = gw_data.get("editable_name")
    description = gw_data.get("description")
    location = gw_data.get("location")
    return {
        "gateway_tti_id": gateway_tti_id,
        "gateway_eui": gateway_eui,
        "frequency_plan": frequency_plan,
        "location": location,
        "description": description,
        "gw_name": gw_name,
    }


def get_node_data_from_things_board(base, tail, device_id, tb_auth):
    """
    Retrieves information about a node from ThingsBoard.

    Parameters:
        base (str): The base URL for the ThingsBoard instance.
        tail (str): The URL tail for the node entity endpoint.
        device_id (str): The device ID for the node.
        tb_auth (str): The authorization token to access ThingsBoard.

    Returns:
        dict: A dictionary containing the retrieved node data.
    """
    try:
        url_tb = construct_url_things_board(base, tail, device_id)
        headers = {"x-authorization": tb_auth, "Content-Type": "application/json"}
        node_data = json.loads(make_request(url_tb, "GET", headers=headers))
    except ValueError as e:
        raise ValueError(f"{str(e)}. Error in retrieving node data from ThingsBoard API in the function "
                         f"get_node_data_from_things_board.")
    except RequestError as e:
        raise RequestError(f"{str(e)}. Error in retrieving node data from ThingsBoard API in the function "
                           f"get_node_data_from_things_board.")
    except Exception as e:
        raise Exception(f"Error in retrieving node data from ThingsBoard API in the function "
                        f"get_node_data_from_things_board: {e}")

    node_id = node_data.get("technology_spec", {}).get("devId")
    node_name = node_data.get("editable_name")
    description = node_data.get("description")
    frequency_plan = node_data.get("technology_spec", {}).get("frequencyPlan")
    node_eui = node_data.get("technology_spec", {}).get("devEUI")
    join_eui = node_data.get("technology_spec", {}).get("joinEUI")
    lorawan_version = node_data.get("technology_spec", {}).get("lorawanVersion")
    sampling_period_sec = node_data.get("sampling_period_sec")
    model = node_data.get("model")
    fw_version = node_data.get("fw_version")
    location = node_data.get("location")

    return {
        "node_id": node_id,
        "node_name": node_name,
        "description": description,
        "frequency_plan": frequency_plan,
        "node_eui": node_eui,
        "join_eui": join_eui,
        "lorawan_version": lorawan_version,
        "sampling_period_sec": sampling_period_sec,
        "model": model,
        "fw_version": fw_version,
        "location": location,
    }


# CMT REQUESTS
def get_all_cmt_clusters(auth):
    """
    Returns a list of all CMT clusters.

    Args:
        auth (str): CMT API authentication token.

    Returns:
        str: A string representing the response body containing a list of all CMT clusters in JSON format.

    Raises:
        HTTPError: If the GET request to the CMT Infrastructure Manager fails.
    """
    try:
        url = construct_url(
            base=CMT_INFRASTRUCTURE_MANAGER_BASE_URL,
            prefix="clusters",
            prefix_id=None,
            list_type_name=None,
            tail=CMT_INFRASTRUCTURE_MANAGER_TAIL_URL,
        )
        return make_request(
            url=url, method="GET", headers={"x-authorization": auth, "Accept": "application/json"}
        )
    except ValueError as e:
        raise ValueError(f"{str(e)}. Error in retrieving clusters data from CMT API in the function "
                         f"get_all_cmt_clusters.")
    except RequestError as e:
        raise RequestError(f"{str(e)}. Error in retrieving clusters data from CMT API in the function "
                           f"get_all_cmt_clusters.")
    except Exception as e:
        raise Exception(f"Error in retrieving clusters data from CMT API in the function "
                        f"get_all_cmt_clusters: {e}")


def get_all_cmt_networks(auth: str) -> str:
    """
    Returns a list of all CMT networks.

    Args:
        auth (str): CMT authentication token.

    Returns:
        str: A JSON string containing the list of all CMT networks.
    """
    # Build the URL using the base URL, prefix, prefix ID, list type name, and tail.
    try:
        url = construct_url(
            base=CMT_INFRASTRUCTURE_MANAGER_BASE_URL,
            prefix="networks",
            prefix_id=None,
            list_type_name=None,
            tail=CMT_INFRASTRUCTURE_MANAGER_TAIL_URL,
        )

        # Make a GET request to the URL with the headers including the CMT authentication token.
        return make_request(
            url=url, method="GET", headers={"x-authorization": auth, "Accept": "application/json"}
        )
    except ValueError as e:
        raise ValueError(f"{str(e)}. Error in retrieving node data from CMT API in the function "
                         f"get_all_cmt_networks.")
    except RequestError as e:
        raise RequestError(f"{str(e)}. Error in retrieving node data from CMT API in the function "
                           f"get_all_cmt_networks.")
    except Exception as e:
        raise Exception(f"Error in retrieving node data from CMT API in the function "
                        f"get_all_cmt_networks: {e}")


def get_all_cmt_cluster_entity(cluster_id, entity_name, auth):
    try:
        url = construct_url(
            base=CMT_INFRASTRUCTURE_MANAGER_BASE_URL,
            prefix="clusters",
            prefix_id=cluster_id,
            list_type_name=entity_name,
            tail=CMT_INFRASTRUCTURE_MANAGER_TAIL_URL,
        )
        return make_request(
            url=url, method="GET", headers={"x-authorization": auth, "Accept": "application/json"}
        )
    except ValueError as e:
        raise ValueError(f"{str(e)}. Error in retrieving node data from CMT API in the function "
                         f"get_all_cmt_cluster_entity.")
    except RequestError as e:
        raise RequestError(f"{str(e)}. Error in retrieving node data from CMT API in the function "
                           f"get_all_cmt_cluster_entity.")
    except Exception as e:
        raise Exception(f"Error in retrieving node data from CMT API in the function "
                        f"get_all_cmt_cluster_entity: {e}")


def get_all_cmt_network_entity(network_id, entity_name, auth):
    try:
        url = construct_url(
            base=CMT_INFRASTRUCTURE_MANAGER_BASE_URL,
            prefix="networks",
            prefix_id=network_id,
            list_type_name=entity_name,
            tail=CMT_INFRASTRUCTURE_MANAGER_TAIL_URL,
        )
        return make_request(
            url=url, method="GET", headers={"x-authorization": auth, "Accept": "application/json"}
        )

    except ValueError as e:
        raise ValueError(f"{str(e)}. Error in retrieving node data from CMT API in the function "
                         f"get_all_cmt_network_entity.")
    except RequestError as e:
        raise RequestError(f"{str(e)}. Error in retrieving node data from CMT API in the function "
                           f"get_all_cmt_network_entity.")
    except Exception as e:
        raise Exception(f"Error in retrieving node data from CMT API in the function "
                        f"get_all_cmt_network_entity: {e}")


# TTI REQUESTS
def get_tti_application_id(network_id):
    try:
        url_app = construct_tti_application_id_url(CMT_INTEGRATION_MANAGER_BASE, network_id)

        headers = {"x-api-key": CMT_INTEGRATION_MANAGER_API_KEY, "Content-Type": "application/json"}
        json_result = json.loads(make_request(url=url_app, method="GET", headers=headers))
        return json_result["data"][0]["serverIdentity"]["applicationId"]

    except ValueError as e:
        raise ValueError(f"{str(e)}. Error in retrieving node data from TTI API in the function "
                         f"get_tti_application_id.")
    except RequestError as e:
        raise RequestError(f"{str(e)}. Error in retrieving node data from TTI API in the function "
                           f"get_tti_application_id.")
    except Exception as e:
        raise TTIException(f"Error in retrieving node data from TTI API in the function "
                           f"get_tti_application_id: {e}")


def get_node_device_addr(tti_app_id, node_dev_id):
    # logger.debug(f"get_node_device_addr")
    try:
        url_addr = construct_device_addr_url(BASE_TTI_NS_ADDRESS, tti_app_id, node_dev_id)
        headers = {"Authorization": TTI_AUTH, "Content-Type": "application/json"}
        response_data = json.loads(make_request(url=url_addr, method="GET", headers=headers))
        return response_data.get("ids", {}).get("dev_addr")
    except ValueError as e:
        raise ValueError(f"{str(e)}. Error in retrieving node data from TTI API in the function "
                         f"get_node_device_addr.")
    except RequestError as e:
        raise RequestError(f"{str(e)}. Error in retrieving node data from TTI API in the function "
                           f"get_node_device_addr.")
    except Exception as e:
        raise TTIException(f"Error in retrieving node data from TTI API in the function "
                           f"get_node_device_addr: {e}")


def make_get_tti_request(url, tti_auth):
    headers = {"Authorization": tti_auth, "Accept": "application/json"}
    try:
        return json.loads(make_request(url, "GET", headers))
    except RequestError as e:
        logger.error(f"{str(e)}. Error in retrieving node data from TTI API in the function "
                     f"make_get_tti_request.")
        raise RequestError(f"{str(e)}. Error in retrieving node data from TTI API in the function "
                           f"make_get_tti_request.")
    except Exception as e:
        logger.error(f"An error occurred in The Things Stack TTI. Function name make_get_tti_request. detail:{str(e)}")
        raise TTIException(
            f"An error occurred in The Things Stack TTI. Function name make_get_tti_request. detail:{str(e)}")


# DATABASE OPERATIONS
def get_cluster_from_db(cluster_id):
    try:
        with Session(db_engine) as session:
            return session.exec(select(Cluster).where(Cluster.cluster_id == cluster_id)).first()
    except Exception as e:
        raise DatabaseError("get_cluster_from_db", str(e))
    finally:
        session.close()


def get_network_from_db(network_id, session: Session):
    try:
        with session:
            return session.exec(select(Network).where(Network.network_id == network_id)).first()
    except Exception as e:
        raise DatabaseError("get_network_from_db", str(e))
    finally:
        session.close()


def get_gateway_from_db(gateway_id, session: Session):
    try:
        with session:
            return session.exec(select(Gateway).where(Gateway.gateway_tb_id == gateway_id)).first()
    except Exception as e:
        raise DatabaseError("get_gateway_from_db", str(e))
    finally:
        session.close()


def get_gateway_from_db_by_tti_id(gateway_id, session: Session):
    try:
        with session:
            return session.exec(select(Gateway).where(Gateway.gateway_tti_id == gateway_id)).first()
    except Exception as e:
        raise DatabaseError("get_gateway_from_db_by_tti_id", str(e))
    finally:
        session.close()


def get_all_gateways_from_db(session: Session):
    try:
        with session:
            return session.exec(select(Gateway)).all()
    except Exception as e:
        raise DatabaseError("get_all_gateways_from_db", str(e))
    finally:
        session.close()


def get_node_from_db(node_id):
    try:
        with Session(db_engine) as session:
            return session.exec(select(Node).where(Node.node_tb_id == node_id)).first()
    except Exception as e:
        raise DatabaseError("get_node_from_db", str(e))
    finally:
        session.close()


def get_application_from_db(application_id, session: Session):
    try:
        with session:
            return session.exec(select(Application).where(Application.application_id == application_id)).first()
    except Exception as e:
        raise DatabaseError("get_application_from_db", str(e))
    finally:
        session.close()


def get_all_application_from_db(session: Session):
    try:
        with session:
            return session.exec(select(Application)).all()
    except Exception as e:
        raise DatabaseError("get_all_application_from_db", str(e))
    finally:
        session.close()


def get_all_deployments_from_db() -> List[DeploymentRead]:
    """
    Get a list of all deployments in the database.

    :param db: The database session.
    :return: A list of all deployments in the database.
    """
    try:
        with Session(db_engine) as session:
            deployments = session.exec(select(Deployment)).all()
            return [DeploymentRead.from_orm(deployment) for deployment in deployments]
    except Exception as e:
        raise DatabaseError("get_all_deployments", str(e))
    finally:
        session.close()


def get_all_network_gateway(network_id: str, session: Session):
    try:
        with session:
            statement = select(Gateway).where(col(Gateway.network_id) == network_id)
            return session.exec(statement).all()

    except Exception as e:
        raise DatabaseError("get_all_network_gateway", str(e))
    finally:
        session.close()


def get_gateways_for_application(application_id: str) -> List[str]:
    logger.debug("get_gateways_for_application")
    try:
        with Session(db_engine) as session:
            query = (
                select(AllRelation.gateway_tti_id)
                .distinct()
                .where(AllRelation.application_id == application_id)
            )
            results = session.exec(query)
            return [row for row in results]

    except Exception as e:
        raise DatabaseError("Error in get_gateways_for_application", str(e))
    finally:
        session.close()
