from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException, status
from sqlmodel import Session

from database.db import get_session
from dependencies.exceptions import EntityNotFound, DatabaseError, QueueSendError
from schemas.help_schemas import MonitoringTaskResult
from services import kpi_monitoring_services

router = APIRouter(prefix="/monitoring")


@router.patch("/gateway/start/{gw_id}", response_model=MonitoringTaskResult)
def start_monitor_gateway(*, gw_id: str, db: Session = Depends(get_session)):
    """
    Endpoint to start monitoring a gateway.
    """
    try:
        return kpi_monitoring_services.start_monitor_gateway(gw_id, db)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to start monitoring gateway: {str(e)}")
    except QueueSendError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to start monitoring gateway: {str(e)}")
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to start monitoring gateway: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to start monitoring gateway: {str(e)}")


@router.patch("/gateway/stop/{gw_id}", response_model=MonitoringTaskResult)
def stop_monitor_gateway(*, gw_id: str, db: Session = Depends(get_session)):
    """
    Endpoint to stop_ monitoring a gateway.
    """
    try:
        return kpi_monitoring_services.stop_monitor_gateway(gw_id, db)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to stop monitoring gateway: {str(e)}")
    except QueueSendError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to stop monitoring gateway: {str(e)}")
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to stop monitoring gateway: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to stop monitoring gateway: {str(e)}")


@router.patch("/gateway/start_all/", response_model=MonitoringTaskResult)
def start_all_gateway(*, db: Session = Depends(get_session)):
    """
    Endpoint to start_all_gateway
    """
    try:
        return kpi_monitoring_services.start_monitor_all_gateway(db)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to start_all_gateway: {str(e)}")
    except QueueSendError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to start_all_gateway: {str(e)}")
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to start_all_gateway: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to start_all_gateway: {str(e)}")


@router.patch("/gateway/stop_all/", response_model=MonitoringTaskResult)
def stop_all_gateway(*, db: Session = Depends(get_session)):
    """
    Endpoint to stop_all_gateway
    """
    try:
        return kpi_monitoring_services.stop_monitor_all_gateway(db)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to stop_all_gateway: {str(e)}")
    except QueueSendError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to stop_all_gateway: {str(e)}")
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to stop_all_gateway: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to stop_all_gateway: {str(e)}")


@router.patch("/network/start/{network_id}", response_model=MonitoringTaskResult)
def start_monitor_network(*, network_id: str, db: Session = Depends(get_session)):
    """
    Endpoint to start_monitor_network
    """
    try:
        return kpi_monitoring_services.start_monitor_network(network_id, db)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to start_monitor_network: {str(e)}")
    except QueueSendError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to start_monitor_network: {str(e)}")
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to start_monitor_network: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to start_monitor_network: {str(e)}")


@router.patch("/network/stop/{network_id}", response_model=MonitoringTaskResult)
def stop_monitor_network(*, network_id: str, db: Session = Depends(get_session)):
    """
    Endpoint to stop_monitor_network
    """
    try:
        return kpi_monitoring_services.stop_monitor_network(network_id, db)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to stop_monitor_network: {str(e)}")
    except QueueSendError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to stop_monitor_network: {str(e)}")
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to stop_monitor_network: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to stop_monitor_network: {str(e)}")


@router.patch("/application/start/{application_id}", response_model=MonitoringTaskResult)
def start_monitor_application(*, application_id: str, db: Session = Depends(get_session)):
    """
    Endpoint to start_monitor_application
    """
    try:
        return kpi_monitoring_services.start_monitor_application(application_id, db)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to start_monitor_application: {str(e)}")
    except QueueSendError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to start_monitor_application: {str(e)}")
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to start_monitor_application: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to start_monitor_application: {str(e)}")


@router.patch("/application/stop/{application_id}", response_model=MonitoringTaskResult)
def stop_monitor_application(*, application_id: str, db: Session = Depends(get_session)):
    """
    Endpoint to stop_monitor_application
    """
    try:
        return kpi_monitoring_services.stop_monitor_application(application_id, db)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to stop_monitor_application: {str(e)}")
    except QueueSendError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to stop_monitor_application: {str(e)}")
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to stop_monitor_application: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to stop_monitor_application: {str(e)}")


@router.patch("/application/start_gateways/{application_id}", response_model=MonitoringTaskResult)
def start_monitor_gateways_of_application(
        *, application_id: str, db: Session = Depends(get_session)
):
    """
    Endpoint to start_monitor_gateways_of_application
    """
    try:
        return kpi_monitoring_services.start_monitor_gateways_of_application(application_id, db)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to start_monitor_gateways_of_application: {str(e)}")
    except QueueSendError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to start_monitor_gateways_of_application: {str(e)}")
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to start_monitor_gateways_of_application: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to start_monitor_gateways_of_application: {str(e)}")


@router.patch("/application/stop_gateways/{application_id}", response_model=MonitoringTaskResult)
def stop_monitor_gateways_of_application(
        *, application_id: str, db: Session = Depends(get_session)
):
    """
    Endpoint to stop_monitor_gateways_of_application
    """
    try:
        return kpi_monitoring_services.stop_monitor_gateways_of_application(application_id, db)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to stop_monitor_gateways_of_application: {str(e)}")
    except QueueSendError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to stop_monitor_gateways_of_application: {str(e)}")
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to stop_monitor_gateways_of_application: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to stop_monitor_gateways_of_application: {str(e)}")


@router.patch("/application/start_all/", response_model=MonitoringTaskResult)
def start_monitor_all_application(*, db: Session = Depends(get_session)):
    """
    Endpoint to start_monitor_all_application
    """
    try:
        return kpi_monitoring_services.start_monitor_all_application(db)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to start_monitor_all_application: {str(e)}")
    except QueueSendError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to start_monitor_all_application: {str(e)}")
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to start_monitor_all_application: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to start_monitor_all_application: {str(e)}")


@router.patch("/application/stop_all/", response_model=MonitoringTaskResult)
def stop_monitor_all_application(*, db: Session = Depends(get_session)):
    """
    Endpoint to stop_monitor_all_application
    """
    try:
        return kpi_monitoring_services.stop_monitor_all_application(db)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to stop_monitor_all_application: {str(e)}")
    except QueueSendError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to stop_monitor_all_application: {str(e)}")
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to stop_monitor_all_application: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to stop_monitor_all_application: {str(e)}")


@router.patch(
    "/application/start_gateways_of_all_applications/", response_model=MonitoringTaskResult
)
def start_monitor_gateways_of_all_applications(
        *, application_ids: List[str], db: Session = Depends(get_session)
):
    """
    Endpoint to start_monitor_gateways_of_all_applications
    """
    try:
        return kpi_monitoring_services.start_monitor_gateways_of_all_applications(
            application_ids, db
        )
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to start_monitor_gateways_of_all_applications: {str(e)}")
    except QueueSendError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to start_monitor_gateways_of_all_applications: {str(e)}")
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to start_monitor_gateways_of_all_applications: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to start_monitor_gateways_of_all_applications: {str(e)}")


@router.patch(
    "/application/stop_gateways_of_all_applications/", response_model=MonitoringTaskResult
)
def stop_monitor_gateways_of_all_applications(
        *, application_ids: List[str], db: Session = Depends(get_session)
):
    """
    Endpoint to stop_monitor_gateways_of_all_applications
    """
    try:
        return kpi_monitoring_services.stop_monitor_gateways_of_all_applications(
            application_ids, db
        )
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to stop_monitor_gateways_of_all_applications: {str(e)}")
    except QueueSendError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Failed to stop_monitor_gateways_of_all_applications: {str(e)}")
    except EntityNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to stop_monitor_gateways_of_all_applications: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to stop_monitor_gateways_of_all_applications: {str(e)}")
