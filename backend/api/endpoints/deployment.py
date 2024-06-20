from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from dependencies.exceptions import EntityNotFound, EntityAlreadyExists, DatabaseError
from database.db import get_session
from schemas.schemas import DeploymentCreate, DeploymentRead, DeploymentUpdate
from services import deployment_services

router = APIRouter(prefix="/deployments")


@router.post("/", response_model=DeploymentRead, status_code=201)
def create_deployment_endpoint(
        deployment: DeploymentCreate, db: Session = Depends(get_session)
):
    """
    Endpoint to create a new deployment.
    """
    try:
        created_deployment = deployment_services.create_deployment(db, deployment)
    except EntityAlreadyExists as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return created_deployment


@router.get("/{deployment_id}", response_model=DeploymentRead)
def read_deployment_endpoint(
        deployment_id: str, db: Session = Depends(get_session)
) -> DeploymentRead:
    """
    Endpoint to read an existing deployment.
    """
    try:
        deployment = deployment_services.read_deployment(deployment_id, db)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return deployment


@router.patch("/{deployment_id}", response_model=DeploymentRead)
def update_deployment_endpoint(
        deployment_id: str, deployment: DeploymentUpdate, db: Session = Depends(get_session)
):
    """
    Endpoint to update an existing deployment.
    """
    try:
        updated_deployment = deployment_services.update_deployment(deployment_id, deployment, db)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return updated_deployment


@router.delete("/{deployment_id}", status_code=204)
def delete_deployment_endpoint(
        deployment_id: str, db: Session = Depends(get_session)
):
    """
    Endpoint to delete an existing deployment.
    """
    try:
        deployment_services.delete_deployment(deployment_id, db)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Response(status_code=status.HTTP_204_NO_CONTENT)
