from fastapi import APIRouter

from .endpoints import clusters
from .endpoints import cmt_connector
from .endpoints import deployment
from .endpoints import gateways
from .endpoints import kpi_monitoring
from .endpoints import networks
from .endpoints import nodes
from .endpoints import tti_connection

api_router = APIRouter()

api_router.include_router(nodes.router, tags=["nodes"])
api_router.include_router(gateways.router, tags=["gateways"])
api_router.include_router(networks.router, tags=["networks"])
api_router.include_router(clusters.router, tags=["clusters"])
api_router.include_router(deployment.router, tags=["deployments"])
api_router.include_router(cmt_connector.router, tags=["cmt_connector"])
api_router.include_router(kpi_monitoring.router, tags=["kpi_monitoring"])
api_router.include_router(tti_connection.router, tags=["tti_connection"])
