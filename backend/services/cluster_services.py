from sqlmodel import Session, select

from backend.dependencies.exceptions import EntityNotFound, EntityAlreadyExists, DatabaseError
from models.models import Cluster
from schemas.schemas import ClusterCreate, ClusterUpdate


def create_cluster(db: Session, cluster_input: ClusterCreate) -> Cluster:
    """
    Create a new cluster in the database.

    :param db: The database session.
    :param cluster_input: The input data for creating the new cluster.
    :return: The newly created cluster.
    :raises EntityAlreadyExists: If the cluster already exists.
    :raises DatabaseError: If there was an error creating the cluster.
    """
    try:
        with db:
            db_cluster = db.exec(
                select(Cluster).where(Cluster.cluster_id == cluster_input.cluster_id)
            ).first()
            if db_cluster:
                raise EntityAlreadyExists(entity_name="Cluster", entity_id=cluster_input.cluster_id)

            new_cluster = Cluster.from_orm(cluster_input)
            db.add(new_cluster)
            db.commit()
            db.refresh(new_cluster)
            return new_cluster
    except EntityAlreadyExists:
        raise  # Re-raise the same exception
    except Exception as e:
        raise DatabaseError(func_name="create_cluster", detail=str(e))


def update_cluster(db: Session, cluster_id: str, new_cluster_data: ClusterUpdate) -> Cluster:
    """
    Update a cluster in the database.

    :param db: The database session.
    :param cluster_id: The ID of the cluster to update.
    :param new_cluster_data: The new data to update the cluster with.
    :return: The updated cluster.
    :raises EntityNotFound: If the cluster does not exist.
    :raises DatabaseError: If there was an error updating the cluster.
    """
    try:
        with db:
            db_cluster = db.exec(select(Cluster).where(Cluster.cluster_id == cluster_id)).first()
            if not db_cluster:
                raise EntityNotFound(entity_name="Cluster", entity_id=cluster_id)

            cluster_data = new_cluster_data.dict(exclude_unset=True)
            for key, value in cluster_data.items():
                setattr(db_cluster, key, value)
            db.commit()
            db.refresh(db_cluster)
            return db_cluster
    except EntityNotFound:
        raise
    except Exception as e:
        raise DatabaseError(func_name="update_cluster", detail=str(e))


def read_cluster(cluster_id: str, db: Session) -> Cluster:
    """
    Get a cluster from the database.

    :param cluster_id: The ID of the cluster to get.
    :param db: The database session.
    :return: The retrieved cluster.
    :raises EntityNotFound: If the cluster does not exist.
    :raises DatabaseError: If there was an error retrieving the cluster.
    """
    try:
        with db:
            db_cluster = db.exec(select(Cluster).where(Cluster.cluster_id == cluster_id)).first()
            if not db_cluster:
                raise EntityNotFound(entity_name="Cluster", entity_id=cluster_id)
            return db_cluster
    except EntityNotFound:
        raise
    except Exception as e:
        raise DatabaseError(func_name="read_cluster", detail=str(e))


def delete_cluster(cluster_id: str, db: Session):
    """
    Delete a cluster from the database.

    :param cluster_id: The ID of the cluster to delete.
    :param db: The database session.
    :raises EntityNotFound: If the cluster does not exist.
    :raises DatabaseError: If there was an error deleting the cluster.
    """
    try:
        with db:
            db_cluster = db.exec(select(Cluster).where(Cluster.cluster_id == cluster_id)).first()
            if not db_cluster:
                raise EntityNotFound(entity_name="Cluster", entity_id=cluster_id)
            db.delete(db_cluster)
            db.commit()
    except EntityNotFound:
        raise
    except Exception as e:
        raise DatabaseError(func_name="delete_cluster", detail=str(e))
