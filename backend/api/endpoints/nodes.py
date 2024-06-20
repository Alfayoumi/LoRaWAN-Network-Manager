from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from backend.dependencies.exceptions import EntityNotFound, EntityAlreadyExists, DatabaseError
from database.db import get_session
from schemas.schemas import NodeCreate, NodeRead, NodeUpdate
from services.node_services import delete_node, update_node, read_node, create_node

router = APIRouter(prefix="/nodes")


@router.post("/", response_model=NodeRead, status_code=201)
def create_node_endpoint(
        node: NodeCreate, db: Session = Depends(get_session)
):
    """
    Endpoint to create a new node.
    """
    try:
        created_node = create_node(db, node)
    except EntityAlreadyExists as e:
        raise HTTPException(status_code=409, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return created_node


@router.get("/{node_id}", response_model=NodeRead)
def read_node_endpoint(
        node_id: str, db: Session = Depends(get_session)
):
    """
    Endpoint to read an existing node.
    """
    try:
        node = read_node(node_id, db)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return node


@router.patch("/{node_id}", response_model=NodeRead)
def update_node_endpoint(
        node_id: str, node: NodeUpdate, db: Session = Depends(get_session)
):
    """
    Endpoint to update an existing node.
    """
    try:
        updated_node = update_node(node_id, node, db)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return updated_node


@router.delete("/{node_id}", status_code=204)
def delete_node_endpoint(
        node_id: str, db: Session = Depends(get_session)
):
    """
    Endpoint to delete an existing node.
    """
    try:
        delete_node(node_id, db)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Response(status_code=status.HTTP_204_NO_CONTENT)
