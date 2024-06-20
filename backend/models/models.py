from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


class NodeBase(SQLModel):
    """
    Schema class representing a node in the system.
    Fields:
        - node_tb_id: A unique identifier for the node.
        - node_dev_id: The device ID assigned to the node.
        - node_dev_addr: The device address assigned to the node.
        - tti_application_id: The Thing Technologies Innovations (TTI) application ID.
        - name: The name of the node.
        - description: A brief description of the node.
        - frequency_plan: The frequency plan used by the node.
        - node_eui: The EUI of the node.
        - join_eui: The EUI used for joining the network.
        - lorawanVersion: The LoRaWAN version used by the node.
        - sampling_period_sec: The period at which the node samples data.
        - model: The model of the node.
        - fw_version: The firmware version running on the node.
        - location: The physical location of the node.
        - network_id: The ID of the network the node is connected to.
    """

    node_dev_id: Optional[str] = Field(index=True)
    node_tb_id: Optional[str] = None
    node_dev_addr: Optional[str] = Field(index=True)
    name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    description: Optional[str] = None
    frequency_plan: Optional[str] = None
    node_eui: Optional[str] = None
    join_eui: Optional[str] = None
    lorawanVersion: Optional[str] = None
    sampling_period_sec: Optional[float] = None
    model: Optional[str] = None
    fw_version: Optional[str] = None
    location: Optional[str] = None
    application_id: Optional[str] = None
    network_id: Optional[str] = None


class GatewayBase(SQLModel):
    """
    Schema class representing a gateway in the system.
    Fields:
        - gateway_tti_id: A unique identifier for the gateway.
        - gateway_tb_id: The Thing Technologies Innovations (TTI) ID assigned to the gateway.
        - name: The name of the gateway.
        - description: A brief description of the gateway.
        - gateway_eui: The EUI of the gateway.
        - frequency_plan: The frequency plan used by the gateway.
        - location: The physical location of the gateway.
        - network_id: The ID of the network the gateway is connected to.
    """

    gateway_tti_id: Optional[str] = None
    gateway_tb_id: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    description: Optional[str] = None
    gateway_eui: Optional[str] = None
    frequency_plan: Optional[str] = None
    location: Optional[str] = None
    network_id: Optional[str] = None


class NetworkBase(SQLModel):
    """
    Schema class representing a network in the system.
    Fields:
        - network_id: A unique identifier for the network.
        - name: The name of the network.
        - tti_application_id: The Thing Technologies Innovations (TTI) application ID.
        - description: A brief description of the network.
        - location: The physical location of the network.
        - cluster_id: The ID of the cluster to which the network belongs.
    """

    network_id: Optional[str] = None
    name: str = Field(index=True)
    description: Optional[str] = None
    location: Optional[str] = None
    application_id: Optional[str] = None
    cluster_id: Optional[str] = None


class ClusterBase(SQLModel):
    """
    Schema class representing a cluster in the system.
    Fields:
        - cluster_id: A unique identifier for the cluster.
        - name: The name of the cluster.
        - description: A brief description of the cluster.
        - location: The physical location of the cluster.
        - deployment_id: The ID of the deployment that the cluster belongs to.
    """

    cluster_id: Optional[str] = None
    name: str = Field(index=True)
    description: Optional[str] = None
    location: Optional[str] = None

    deployment_id: Optional[str] = None


class DeploymentBase(SQLModel):
    """
    Schema class representing a deployment in the system.
    Fields:
        - deployment_id: A unique identifier for the deployment.
        - name: The name of the deployment.
        - description: A brief description of the deployment.
    """

    deployment_id: Optional[str] = None
    name: str = Field(index=True)
    description: Optional[str] = None


class ApplicationBase(SQLModel):
    """
    Schema class representing an application in the system.
    Fields:
        - application_id: A unique identifier for the application.
        - created_at: The timestamp indicating the creation time of the application.
        - updated_at: The timestamp indicating the last update time of the application.
    """

    application_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Node(NodeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class Gateway(GatewayBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class Network(NetworkBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class Cluster(ClusterBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class Deployment(DeploymentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class Application(ApplicationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class AllRelation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: Optional[str] = None
    dev_addr: Optional[str] = None
    last_f_cnt: Optional[str] = None
    application_id: Optional[str] = None
    gateway_tti_id: Optional[str] = None
