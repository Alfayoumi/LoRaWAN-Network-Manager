from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response, status
from sqlmodel import Session

from database.db import get_session
from dependencies.exceptions import EntityAlreadyExists, DatabaseError, EntityNotFound
from schemas.schemas import NetworkCreate
from schemas.schemas import NetworkRead
from schemas.schemas import NetworkUpdate
from services.network_services import create_network, read_network, update_network, delete_network

router = APIRouter(prefix="/networks")


@router.post("/", response_model=NetworkRead, status_code=201)
def create_network_endpoint(*, db: Session = Depends(get_session), network: NetworkCreate):
    """
    Endpoint to create a new network.
    """
    try:
        created_network = create_network(db, network)
    except EntityAlreadyExists as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return created_network


@router.get("/{network_id}", response_model=NetworkRead)
def read_network_endpoint(*, db: Session = Depends(get_session), network_id: str):
    """
    Endpoint to read an existing network.
    """
    try:
        network = read_network(network_id, db)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return network


@router.patch("/{network_id}", response_model=NetworkRead)
def update_network_endpoint(*, db: Session = Depends(get_session), network_id: str, network: NetworkUpdate):
    """
    Endpoint to update an existing network.
    """
    try:
        updated_network = update_network(network_id, network, db)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return updated_network


@router.delete("/{network_id}", status_code=204)
def delete_network_endpoint(*, db: Session = Depends(get_session), network_id: str):
    """
    Endpoint to delete an existing network.
    """
    try:
        delete_network(network_id, db)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
