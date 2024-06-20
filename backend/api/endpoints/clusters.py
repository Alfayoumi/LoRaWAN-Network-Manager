from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response, status
from sqlmodel import Session

from database.db import get_session
from schemas.schemas import ClusterCreate
from schemas.schemas import ClusterRead
from schemas.schemas import ClusterUpdate
from services import cluster_services
from services.cluster_services import (
    DatabaseError,
    EntityNotFound,
    EntityAlreadyExists,
)

router = APIRouter(prefix="/clusters")


@router.post("/", response_model=ClusterRead, status_code=status.HTTP_201_CREATED)
def create_cluster(cluster: ClusterCreate, db: Session = Depends(get_session)):
    """
    Create a new cluster.

    :param cluster: ClusterCreate schema
    :param db: Session from the get_session dependency
    :return: ClusterRead schema or HTTPException
    """
    try:
        created_cluster = cluster_services.create_cluster(db, cluster)
        return created_cluster
    except EntityAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cluster_id}", response_model=ClusterRead)
def read_cluster(cluster_id: str, db: Session = Depends(get_session)):
    """
    Retrieve a specific cluster by ID.

    :param cluster_id: Cluster ID to retrieve
    :param db: Session from the get_session dependency
    :return: ClusterRead schema or HTTPException
    """
    try:
        cluster = cluster_services.read_cluster(cluster_id, db)
        return cluster
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{cluster_id}", response_model=ClusterRead)
def update_cluster(cluster_id: str, cluster: ClusterUpdate, db: Session = Depends(get_session)):
    """
    Update an existing cluster by ID.

    :param cluster_id: Cluster ID to update
    :param cluster: ClusterUpdate schema
    :param db: Session from the get_session dependency
    :return: ClusterRead schema or HTTPException
    """

    try:
        updated_cluster = cluster_services.update_cluster(db, cluster_id, cluster)
        return updated_cluster
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{cluster_id}", status_code=204)
def delete_cluster(cluster_id: str, db: Session = Depends(get_session)):
    """
    Delete an existing cluster by ID.

    :param cluster_id: Cluster ID to delete
    :param db: Session from the get_session dependency
    :return: Status message or HTTPException
    """
    try:
        cluster_services.delete_cluster(cluster_id, db)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))
