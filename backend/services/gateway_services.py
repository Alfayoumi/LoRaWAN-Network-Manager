from sqlmodel import Session, select

from backend.dependencies.exceptions import EntityNotFound, EntityAlreadyExists, DatabaseError
from dependencies import utility_functions
from dependencies.config import logger_config
from models.models import Gateway
from models.models import GatewayBase
from schemas.schemas import GatewayCreate

logger = utility_functions.get_logger(logger_config)


def create_gateway(db: Session, gateway_input: GatewayCreate) -> Gateway:
    """
    Create a new gateway in the database.

    :param db: The database session.
    :param gateway_input: The gateway input data.
    :return: The newly created gateway.
    :raises EntityAlreadyExists: If the gateway already exists.
    :raises DatabaseError: If there was an error creating the gateway.
    """
    logger.debug(f"create_gateway")
    try:
        with db:
            db_gateway = db.exec(
                select(Gateway).where(Gateway.gateway_tti_id == gateway_input.gateway_tti_id)
            ).first()
            if db_gateway:
                raise EntityAlreadyExists(entity_name="Gateway", entity_id=gateway_input.gateway_tti_id)

            new_gateway = Gateway.from_orm(gateway_input)
            db.add(new_gateway)
            db.commit()
            db.refresh(new_gateway)
            return new_gateway
    except EntityAlreadyExists:
        raise  # Re-raise the same exception
    except Exception as e:
        raise DatabaseError(func_name="create_gateway", detail=str(e))


def update_gateway(gateway_tti_id: str, new_gateway_data: GatewayBase, db: Session) -> Gateway:
    """
    Update a gateway in the database.

    :param gateway_tti_id:
    :param new_gateway_data: The updated gateway data.
    :param db: The database session.
    :return: The updated gateway.
    :raises EntityNotFound: If the gateway does not exist.
    :raises DatabaseError: If there was an error updating the gateway.
    """
    try:
        with db:
            statement = select(Gateway).where(
                Gateway.gateway_tti_id == new_gateway_data.gateway_tti_id
            )
            db_gateway = db.exec(statement).first()
            if not db_gateway:
                raise EntityNotFound(entity_name="Gateway", entity_id=gateway_tti_id)

            gateway_data = new_gateway_data.dict(exclude_unset=True)
            for key, value in gateway_data.items():
                setattr(db_gateway, key, value)

            db.add(db_gateway)
            db.commit()
            db.refresh(db_gateway)
            return db_gateway
    except EntityNotFound:
        raise  # Re-raise the same exception
    except Exception as e:
        raise DatabaseError(func_name="update_gateway", detail=str(e))


def read_gateway(gateway_id: str, db: Session) -> Gateway:
    """
    Get a gateway from the database.

    :param gateway_id: The ID of the gateway to retrieve.
    :param db: The database session.
    :return: The requested gateway.
    :raises EntityNotFound: If the gateway does not exist.
    :raises DatabaseError: If there was an error retrieving the gateway.
    """
    try:
        db_gateway = db.get(Gateway, gateway_id)
        if not db_gateway:
            raise EntityNotFound(entity_name="Gateway", entity_id=gateway_id)
        return db_gateway
    except EntityNotFound:
        raise  # Re-raise the same exception
    except Exception as e:
        raise DatabaseError(func_name="read_gateway", detail=str(e))


def delete_gateway(gateway_id: str, db: Session) -> dict:
    """
    Delete a gateway from the database.

    :param gateway_id: The ID of the gateway to delete.
    :param db: The database session.
    :return: A dictionary with the 'ok' key set to True if the gateway was deleted.
    :raises EntityNotFound: If the gateway does not exist.
    :raises DatabaseError: If there was an error deleting the gateway.
    """
    try:
        gateway = db.get(Gateway, gateway_id)
        if not gateway:
            raise EntityNotFound(entity_name="Gateway", entity_id=gateway_id)

        db.delete(gateway)
        db.commit()
        return {"ok": True}
    except EntityNotFound:
        raise  # Re-raise the same exception
    except Exception as e:
        raise DatabaseError(func_name="delete_gateway", detail=str(e))
