from fastapi import APIRouter, Depends
from fastapi import Response, status
from fastapi.exceptions import HTTPException
from sqlmodel import Session
from database.db import get_session
from dependencies.exceptions import EntityAlreadyExists, DatabaseError, EntityNotFound
from schemas.schemas import ApplicationCreate, ApplicationRead, ApplicationUpdate
from services.application_services import ApplicationService

router = APIRouter(prefix="/applications")


@router.post("/", response_model=ApplicationRead, status_code=201)
def create_application_handler(
    application: ApplicationCreate,
    db: Session = Depends(get_session),
):
    """
    Endpoint to create a new application.
    """
    try:
        created_application = ApplicationService.create_application(db, application)
    except EntityAlreadyExists as e:
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return created_application


@router.get("/{application_id}", response_model=ApplicationRead)
def read_application_handler(application_id: str, db: Session = Depends(get_session)):
    """
    Endpoint to read an existing application by ID.
    """
    try:
        application = ApplicationService.read_application(db, application_id)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return application


@router.put("/{application_id}", response_model=ApplicationRead)
def update_application_handler(
    application_id: str,
    application: ApplicationUpdate,
    db: Session = Depends(get_session),
):
    """
    Endpoint to update an existing application.
    """
    try:
        updated_application = ApplicationService.update_application(db, application_id, application)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return updated_application


@router.delete("/{application_id}", status_code=204)
def delete_application_handler(
    application_id: str,
    db: Session = Depends(get_session),
):
    """
    Endpoint to delete an existing application.
    """
    try:
        ApplicationService.delete_application(db, application_id)
    except EntityNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Response(status_code=status.HTTP_204_NO_CONTENT)
