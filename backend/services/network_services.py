from sqlmodel import Session, select

from backend.dependencies.exceptions import EntityNotFound, EntityAlreadyExists, DatabaseError
from models.models import Network
from schemas.schemas import NetworkCreate, NetworkUpdate


def create_network(db: Session, network_input: NetworkCreate) -> Network:
    """
    Creates a new network and adds it to the database.

    :param db: The database session.
    :param network_input: The data for the new network.
    :return: The newly created network object.
    :raises EntityAlreadyExists: If a network with the same ID already exists.
    :raises DatabaseError: If there was an error adding the network to the database.
    """
    try:
        with db:
            db_network = db.exec(
                select(Network).where(Network.network_id == network_input.network_id)
            ).first()
            if db_network:
                raise EntityAlreadyExists(entity_name="Network", entity_id=network_input.network_id)

            new_network = Network.from_orm(network_input)
            db.add(new_network)
            db.commit()
            db.refresh(new_network)
            return new_network
    except EntityAlreadyExists:
        raise
    except Exception as e:
        raise DatabaseError(func_name="create_network", detail=str(e))


def update_network(network_id: str, new_network_data: NetworkUpdate, db: Session) -> Network:
    """
    Updates an existing network in the database.

    :param network_id: The ID of the network to update.
    :param new_network_data: The updated data for the network.
    :param db: The database session.
    :return: The updated network object.
    :raises EntityNotFound: If the network could not be found in the database.
    :raises DatabaseError: If there was an error updating the network in the database.
    """
    try:
        with db:
            db_network = db.exec(select(Network).where(Network.network_id == network_id)).first()
            if not db_network:
                raise EntityNotFound(entity_name="Network", entity_id=network_id)
            network_data = new_network_data.dict(exclude_unset=True)
            for key, value in network_data.items():
                setattr(db_network, key, value)
            db.add(db_network)
            db.commit()
            db.refresh(db_network)
            return db_network
    except EntityNotFound:
        raise
    except Exception as e:
        raise DatabaseError(func_name="update_network", detail=str(e))


def read_network(network_id: str, db: Session) -> Network:
    """
    Retrieves a network from the database.

    :param network_id: The ID of the network to retrieve.
    :param db: The database session.
    :return: The network object with the specified ID.
    :raises EntityNotFound: If the network could not be found in the database.
    :raises DatabaseError: If there was an error retrieving the network from the database.
    """
    try:
        with db:
            db_network = db.exec(select(Network).where(Network.network_id == network_id)).first()
            if not db_network:
                raise EntityNotFound(entity_name="Network", entity_id=network_id)
            return db_network
    except EntityNotFound:
        raise
    except Exception as e:
        raise DatabaseError(func_name="read_network", detail=str(e))


def delete_network(network_id: str, db: Session):
    """
    Deletes a network from the database.

    :param network_id: The ID of the network to delete.
    :param db: The database session.
    :return: A dictionary indicating whether the operation was successful.
    :raises EntityNotFound: If the network could not be found in the database.
    :raises DatabaseError: If there was an error deleting the network from the database.
    """
    try:
        with db:
            network = db.exec(select(Network).where(Network.network_id == network_id)).first()
            if not network:
                raise EntityNotFound(entity_name="Network", entity_id=network_id)
            db.delete(network)
            db.commit()
    except EntityNotFound:
        raise
    except Exception as e:
        raise DatabaseError(func_name="delete_network", detail=str(e))
