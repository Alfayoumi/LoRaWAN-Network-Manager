import json
import os

from sqlmodel import Session

from dependencies import utility_functions
from dependencies.config import logger_config
from models.models import Cluster
from models.models import Gateway
from models.models import Network
from models.models import Node
from .utility_services import CMT_INFRASTRUCTURE_MANAGER_BASE_URL, get_network_from_db, get_cluster_from_db, \
    get_gateway_from_db, get_node_from_db, get_all_deployments_from_db
from .utility_services import CMT_INFRASTRUCTURE_MANAGER_TAIL_URL
from .utility_services import TB_BASE_URL
from .utility_services import TB_TAIL_URL
from .utility_services import get_all_cmt_cluster_entity
from .utility_services import get_all_cmt_clusters
from .utility_services import get_all_cmt_network_entity
from .utility_services import get_all_cmt_networks
from .utility_services import get_gateway_data_from_things_board
from .utility_services import get_node_data_from_things_board
from .utility_services import get_node_device_addr
from .utility_services import get_tti_application_id

logger = utility_functions.get_logger(logger_config)


def add_new_db_node(db: Session, network_id: str, node_data: dict, tb_auth: str) -> None:
    """
    Add a new node to the database.

    :param db: The database session.
    :param network_id: The ID of the network to which the node belongs.
    :param node_data: The node data returned by TB API.
    :param tb_auth: The authorization token for accessing TB API.
    :raises ValueError: If any required input data is missing or invalid.
    :raises Exception: If there was an error adding the node to the database.
    """

    if not isinstance(network_id, str):
        raise ValueError("Network ID must be a string")
    if not isinstance(tb_auth, str) or not tb_auth.strip():
        raise ValueError("TB authorization token must be a non-empty string")

    try:
        tb_node_data = get_node_data_from_things_board(
            CMT_INFRASTRUCTURE_MANAGER_BASE_URL,
            CMT_INFRASTRUCTURE_MANAGER_TAIL_URL,
            node_data["id"],
            tb_auth,
        )
        tti_app_id = get_tti_application_id(network_id=network_id)
        node_dev_addr = get_node_device_addr(tti_app_id, tb_node_data["node_id"])
        new_node = Node(
            node_tb_id=node_data["id"],
            node_dev_id=tb_node_data["node_id"],
            node_dev_addr=node_dev_addr,
            tti_application_id=tti_app_id,
            name=tb_node_data["node_name"],
            description=tb_node_data["description"],
            frequency_plan=tb_node_data["frequency_plan"],
            node_eui=tb_node_data["node_eui"],
            join_eui=tb_node_data["join_eui"],
            lorawanVersion=tb_node_data["lorawanVersion"],
            sampling_period_sec=tb_node_data["sampling_period_sec"],
            model=tb_node_data["model"],
            fw_version=tb_node_data["fw_version"],
            location=tb_node_data["location"],
            network_id=network_id,
        )

        db.add(new_node)
        db.commit()
        db.refresh(new_node)
    except Exception as e:
        raise Exception(f"Error adding node to database: {str(e)}")


def update_node(db: Session, network_id, node_data, tb_auth):
    logger.debug("update_node ")

    db_node = get_node_from_db(node_data["id"])
    if not db_node:
        add_new_db_node(db, network_id, node_data, tb_auth)


def update_network_nodes(db: Session, cmt_auth, tb_auth, network_id):
    logger.debug("update_network_nodes ")
    all_network_nodes = get_all_cmt_network_entity(network_id, "nodes", cmt_auth)
    json_message = json.loads(all_network_nodes)
    data = json_message["data"]
    for node in data:
        update_node(db, network_id, node, tb_auth)


def add_new_gateway(db: Session, network_id, gateway_data, tb_auth):
    logger.debug("add_new_gateway ")
    tb_gateway_data = get_gateway_data_from_things_board(
        TB_BASE_URL,
        TB_TAIL_URL,
        gateway_data["id"],
        tb_auth,
    )

    new_gateway = Gateway(
        gateway_tb_id=gateway_data["id"],
        gateway_tti_id=tb_gateway_data["gateway_tti_id"],
        name=tb_gateway_data["gw_name"],
        description=tb_gateway_data["description"],
        gateway_eui=tb_gateway_data["gateway_eui"],
        frequency_plan=tb_gateway_data["frequency_plan"],
        location=tb_gateway_data["location"],
        network_id=network_id,
    )
    db.add(new_gateway)
    db.commit()
    db.refresh(new_gateway)


def update_gateway(db: Session, network_id, gateway_data, tb_auth):
    logger.debug("update_gateway")
    db_gateway = get_gateway_from_db(gateway_data["id"])
    if not db_gateway:
        add_new_gateway(db, network_id, gateway_data, tb_auth)


def update_network_gateways(db: Session, cmt_auth, tb_auth, network_id):
    logger.debug("update_network_gateways")

    all_network_gateways = get_all_cmt_network_entity(network_id, "gateways", cmt_auth)
    json_message = json.loads(all_network_gateways)
    data = json_message["data"]
    for gateway in data:
        update_gateway(db, network_id, gateway, tb_auth)


def add_new_network(db: Session, network_data):
    logger.debug("add_new_network ")
    network = db.get(Network, network_data["id"])
    if not network:
        tti_app_id = get_tti_application_id(network_id=network_data["id"])
        new_network = Network(
            network_id=network_data["id"],
            name=network_data["name"],
            tti_application_id=tti_app_id,
            description=network_data["description"],
            locations=network_data["location"],
            cluster_id=None,
        )
        db.add(new_network)
        db.commit()
        db.refresh(new_network)


def update_network(db: Session, cmt_auth: str, tb_auth: str):
    logger.debug("update_network")

    cmt_networks = get_all_cmt_networks(cmt_auth)
    json_message = json.loads(cmt_networks)
    data = json_message["data"]
    for network in data:
        db_network = db.get(Network, network["id"])
        if not db_network:
            add_new_network(db, network)
            update_network_gateways(db, cmt_auth, tb_auth, network["id"])
            update_network_nodes(db, cmt_auth, tb_auth, network["id"])


def add_new_network_to_cluster(db: Session, cluster_id, network_data):
    logger.debug(f"add_new_network_to_cluster")
    network = get_network_from_db(network_data["id"])
    if not network:
        tti_app_id = get_tti_application_id(network_id=network_data["id"])
        new_network = Network(
            network_id=network_data["id"],
            name=network_data["name"],
            tti_application_id=tti_app_id,
            description=network_data["description"],
            locations=network_data["location"],
            cluster_id=cluster_id,
        )
        db.add(new_network)
        db.commit()
        db.refresh(new_network)


def update_cluster_networks(db: Session, cmt_auth, tb_auth, cluster_id):
    logger.debug(f"update_cluster_networks")
    all_cluster_networks = get_all_cmt_cluster_entity(cluster_id, "networks", cmt_auth)
    json_message = json.loads(all_cluster_networks)
    data = json_message["data"]
    for network in data:
        # db_network = db.get(Network, network["id"])
        db_network = get_network_from_db(network["id"])
        if not db_network:
            add_new_network_to_cluster(db, cluster_id, network)
            update_network_gateways(db, cmt_auth, tb_auth, network["id"])
            update_network_nodes(db, cmt_auth, tb_auth, network["id"])


def add_new_cluster(db: Session, deployment_id, cluster_data):
    new_cluster = Cluster(
        cluster_id=cluster_data["id"],
        name=cluster_data["name"],
        description=cluster_data["description"],
        locations=cluster_data["location"],
        deployment_id=deployment_id,
    )
    db.add(new_cluster)
    db.commit()
    db.refresh(new_cluster)


def update_cluster(db: Session, deployment_id: str, cmt_auth: str, tb_auth: str):
    logger.debug(f"update_cluster")

    cmt_clusters = json.loads(get_all_cmt_clusters(cmt_auth))
    data = cmt_clusters["data"]
    for cluster in data:
        db_cluster = get_cluster_from_db(cluster["id"])
        if not db_cluster:
            add_new_cluster(db, deployment_id, cluster)
            update_cluster_networks(db, cmt_auth, tb_auth, cluster["id"])


def update_data_architecture_from_cmt(db: Session, cmt_auth: str, tb_auth: str):
    logger.debug(f"update_data_architecture_from_cmt")
    deployment_id = str(os.getenv("DEPLOYMENT_ID"))
    update_cluster(db, deployment_id, cmt_auth, tb_auth)
    logger.debug("update_data_architecture_from_cmt Done!")
