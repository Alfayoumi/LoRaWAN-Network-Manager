from sqlmodel import Session, select

from backend.dependencies.exceptions import EntityNotFound, EntityAlreadyExists, DatabaseError
from dependencies import utility_functions
from dependencies.config import logger_config
from models.models import Node
from models.models import NodeBase
from schemas.schemas import NodeUpdate

logger = utility_functions.get_logger(logger_config)


def create_node(db: Session, node_input: NodeBase) -> Node:
    """
    Creates a new node in the database.

    :param db: The database session.
    :param node_input: The node data to be created.
    :return: The newly created node.
    :raises EntityAlreadyExists: If a node with the same node_input already exists in the database.
    :raises DatabaseError: If there is an error creating the node in the database.
    """
    try:
        with db:
            db_node = db.exec(select(Node).where(Node.node_eui == node_input.node_eui)).first()
            if db_node:
                raise EntityAlreadyExists(entity_name="Node", entity_id=node_input.node_eui)

            new_node = Node.from_orm(node_input)
            db.add(new_node)
            db.commit()
            db.refresh(new_node)
            return new_node
    except EntityAlreadyExists:
        raise  # Re-raise the same exception
    except Exception as e:
        raise DatabaseError(func_name="create_node", detail=str(e))


def update_node(node_eui: str, new_node_data: NodeUpdate, db: Session) -> Node:
    """
    Updates an existing node in the database.

    :param node_eui:
    :param new_node_data: The updated node data.
    :param db: The database session.
    :raises EntityNotFound: If the node is not found in the database.
    :raises DatabaseError: If there is an error updating the node in the database.
    :return: The updated node.
    """
    logger.debug("update_node ")
    try:
        with db:
            db_node = db.exec(select(Node).where(Node.node_eui == new_node_data.node_eui)).first()
            if not db_node:
                raise EntityNotFound(entity_name="Node", entity_id=node_eui)
            node_data = new_node_data.dict(exclude_unset=True)
            for key, value in node_data.items():
                setattr(db_node, key, value)
            db.commit()
            db.refresh(db_node)
            return db_node
    except EntityNotFound:
        raise  # Re-raise the same exception
    except Exception as e:
        raise DatabaseError(func_name="update_node", detail=str(e))


def read_node(node_id: str, db: Session) -> Node:
    """
    Retrieves an existing node from the database.

    :param node_id: The ID of the node to be retrieved.
    :param db: The database session.
    :raises EntityNotFound: If the node is not found in the database.
    :raises DatabaseError: If there is an error retrieving the node from the database.
    :return: The retrieved node.
    """
    try:
        with db:
            db_node = db.exec(select(Node).where(Node.node_eui == node_id)).first()
            if not db_node:
                raise EntityNotFound(entity_name="Node", entity_id=node_id)
            return db_node
    except EntityNotFound:
        raise  # Re-raise the same exception
    except Exception as e:
        raise DatabaseError(func_name="read_node", detail=str(e))


def delete_node(node_id: str, db: Session) -> dict:
    """
    Deletes a node from the database.

    :param node_id: The ID of the node to be deleted.
    :param db: The database session.
    :raises EntityNotFound: If the node is not found in the database.
    :raises DatabaseError: If there is an error deleting the node from the database.
    :return: A dictionary indicating success or failure of the deletion.
    """
    try:
        with db:
            db_node = db.exec(select(Node).where(Node.node_eui == node_id)).first()
            if not db_node:
                raise EntityNotFound(entity_name="Node", entity_id=node_id)
            db.delete(db_node)
            db.commit()
            return {"ok": True}
    except EntityNotFound:
        raise  # Re-raise the same exception
    except Exception as e:
        raise DatabaseError(func_name="delete_node", detail=str(e))
