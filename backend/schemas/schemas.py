from typing import Optional
from pydantic import BaseModel

from models.models import ApplicationBase
from models.models import ClusterBase
from models.models import DeploymentBase
from models.models import GatewayBase
from models.models import NetworkBase
from models.models import NodeBase


class NodeCreate(NodeBase):
    """Schema for creating a new node."""

    pass


class NodeRead(NodeBase):
    """Schema for reading an existing node."""

    pass


class NodeUpdate(BaseModel):
    """Schema for updating an existing node."""

    node_dev_id: Optional[str] = None
    node_tb_id: Optional[str] = None
    node_dev_addr: Optional[str] = None
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


class GatewayCreate(GatewayBase):
    """Schema for creating a new gateway."""

    pass


class GatewayRead(GatewayBase):
    """Schema for reading an existing gateway."""

    pass


class GatewayUpdate(GatewayBase):
    """Schema for updating an existing gateway."""

    pass


class NetworkCreate(NetworkBase):
    """Schema for creating a new network."""

    pass


class NetworkRead(NetworkBase):
    """Schema for reading an existing network."""

    pass


class NetworkUpdate(BaseModel):
    """Schema for updating an existing network."""

    network_id: Optional[str] = None  # ID of the network
    name: Optional[str] = None  # Name of the network
    application_id: Optional[str] = None  # TTI application ID of the network
    description: Optional[str] = None  # Description of the network
    location: Optional[str] = None  # Location of the network


class ClusterCreate(ClusterBase):
    """Schema for creating a new cluster."""

    pass


class ClusterRead(ClusterBase):
    """Schema for reading an existing cluster."""

    pass


class ClusterUpdate(BaseModel):
    """Schema for updating an existing cluster."""

    cluster_id: Optional[str] = None  # ID of the cluster
    name: Optional[str] = None  # Name of the cluster
    description: Optional[str] = None  # Description of the cluster
    location: Optional[str] = None  # Location of the cluster


class DeploymentCreate(DeploymentBase):
    """Schema for creating a new deployment."""

    pass


class DeploymentRead(DeploymentBase):
    """Schema for reading an existing deployment."""

    pass


class DeploymentUpdate(BaseModel):
    """Schema for updating an existing deployment."""

    deployment_id: Optional[str] = None  # ID of the deployment
    name: Optional[str] = None  # Name of the deployment
    description: Optional[str] = None  # Description of the deployment


class ApplicationCreate(ApplicationBase):
    """Schema for creating a new Application."""

    pass


class ApplicationRead(ApplicationBase):
    """Schema for reading an existing Application."""

    pass


class ApplicationUpdate(ApplicationBase):
    """Schema for updating an existing Application."""

    pass
