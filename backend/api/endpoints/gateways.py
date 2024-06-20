from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from database.db import get_session
from dependencies.exceptions import EntityNotFound, EntityAlreadyExists, DatabaseError
from schemas.schemas import GatewayCreate, GatewayRead, GatewayUpdate
from services.gateway_services import create_gateway, delete_gateway, update_gateway, read_gateway

router = APIRouter(prefix="/gateways")


@router.post("/", response_model=GatewayRead, status_code=201)
def create_gateway_endpoint(
        gateway: GatewayCreate, db: Session = Depends(get_session)
):
    """
    Endpoint to create a new gateway.
    """
    try:
        created_gateway = create_gateway(db, gateway)
    except EntityAlreadyExists as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return created_gateway


@router.get("/{gateway_id}", response_model=GatewayRead)
def read_gateway_endpoint(
        gateway_id: str, db: Session = Depends(get_session)
):
    """
    Endpoint to read an existing gateway.
    """
    try:
        gateway = read_gateway(gateway_id, db)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return gateway


@router.patch("/{gateway_id}", response_model=GatewayRead)
def update_gateway_endpoint(
        gateway_id: str, gateway: GatewayUpdate, db: Session = Depends(get_session)
):
    """
    Endpoint to update an existing gateway.
    """
    try:
        updated_gateway = update_gateway(gateway_id, gateway, db)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return updated_gateway


@router.delete("/{gateway_id}")
def delete_gateway_endpoint(
        gateway_id: str, db: Session = Depends(get_session)
):
    """
    Endpoint to delete an existing gateway.
    """
    try:
        delete_gateway(gateway_id, db)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Response(status_code=status.HTTP_204_NO_CONTENT)
