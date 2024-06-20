from sqlmodel import Session, select

from backend.dependencies.exceptions import EntityNotFound, EntityAlreadyExists, DatabaseError
from models.models import Deployment
from schemas.schemas import DeploymentCreate, DeploymentUpdate


def create_deployment(db: Session, deployment_input: DeploymentCreate) -> Deployment:
    """
    Adds a new deployment to the database.

    Args:
        db (Session): The database session.
        deployment_input (DeploymentCreate): A `DeploymentCreate` instance representing the new deployment.

    Returns:
        Deployment: The new `Deployment` instance created in the database.

    Raises:
        EntityAlreadyExists: If the deployment already exists.
        DatabaseError: If there was an error adding the deployment to the database.
    """
    try:
        with db:
            db_deployment = db.exec(
                select(Deployment).where(Deployment.deployment_id == deployment_input.deployment_id)
            ).first()
            if db_deployment:
                raise EntityAlreadyExists(entity_name="Deployment", entity_id=deployment_input.deployment_id)

            new_deployment = Deployment.from_orm(deployment_input)
            db.add(new_deployment)
            db.commit()
            db.refresh(new_deployment)
            return new_deployment
    except EntityAlreadyExists:
        raise
    except Exception as e:
        raise DatabaseError(func_name="create_deployment", detail=str(e))


def update_deployment(deployment_id: str, new_deployment_data: DeploymentUpdate, db: Session) -> Deployment:
    """
    Update an existing deployment record in the database with the provided new data.

    :param deployment_id: The ID of the deployment to update.
    :param new_deployment_data: The new deployment data to update the record with.
    :param db: The database session.
    :raises EntityNotFound: If no deployment with the given ID is found in the database.
    :raises DatabaseError: If there was an error updating the deployment in the database.
    :return: The updated deployment record.
    """
    try:
        with db:
            db_deployment = db.exec(
                select(Deployment).where(Deployment.deployment_id == deployment_id)
            ).first()
            if not db_deployment:
                raise EntityNotFound(entity_name="Deployment", entity_id=deployment_id)

            # Update the deployment record with the new data
            deployment_data = new_deployment_data.dict(exclude_unset=True)
            for key, value in deployment_data.items():
                setattr(db_deployment, key, value)

            # Save the updated deployment record to the database
            db.add(db_deployment)
            db.commit()
            db.refresh(db_deployment)

            # Return the updated deployment record
            return db_deployment
    except EntityNotFound:
        raise
    except Exception as e:
        raise DatabaseError(func_name="update_deployment", detail=str(e))


def read_deployment(deployment_id: str, db: Session):
    """
    Read a deployment from the database by ID.

    :param deployment_id: The ID of the deployment to read.
    :param db: The database session.
    :return: The Deployment object for the specified ID.
    :raises EntityNotFound: If no deployment is found for the specified ID.
    :raises DatabaseError: If there was an error retrieving the deployment from the database.
    """
    try:
        with db:
            db_deployment = db.exec(
                select(Deployment).where(Deployment.deployment_id == deployment_id)
            ).first()
            if not db_deployment:
                raise EntityNotFound(entity_name="Deployment", entity_id=deployment_id)

            # Return the updated deployment record
            return db_deployment
    except EntityNotFound:
        raise
    except Exception as e:
        raise DatabaseError(func_name="read_deployment", detail=str(e))


def delete_deployment(deployment_id: str, db: Session):
    """
    Deletes a deployment from the database.

    :param deployment_id: The ID of the deployment to delete.
    :param db: The database session.
    :raises EntityNotFound: If no deployment is found with the given ID.
    :raises DatabaseError: If there was an error deleting the deployment from the database.
    """
    try:
        with db:
            db_deployment = db.exec(
                select(Deployment).where(Deployment.deployment_id == deployment_id)
            ).first()
            if not db_deployment:
                raise EntityNotFound(entity_name="Deployment", entity_id=deployment_id)
            db.delete(db_deployment)
            db.commit()
    except EntityNotFound:
        raise
    except Exception as e:
        raise DatabaseError(func_name="delete_deployment", detail=str(e))
