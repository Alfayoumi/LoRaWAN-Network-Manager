from typing import List

from sqlmodel import Session
from sqlmodel import select

from backend.dependencies.exceptions import EntityAlreadyExists, EntityNotFound, DatabaseError
from dependencies import utility_functions
from dependencies.config import logger_config
from models.models import Application
from models.models import ApplicationBase
from schemas.schemas import ApplicationRead

logger = utility_functions.get_logger(logger_config)


class ApplicationService:
    @staticmethod
    def create_application(db: Session, application_input: ApplicationBase) -> Application:
        """
        Create a new application in the database.

        :param db: The database session.
        :param application_input: The input data for creating the new application.
        :return: The newly created application.
        :raises EntityAlreadyExists: If the application already exists.
        :raises DatabaseError: If there was an error creating the application.
        """
        try:
            with db:
                db_application = db.exec(
                    select(Application).where(
                        Application.application_id == application_input.application_id
                    )
                ).first()
                if db_application:
                    raise EntityAlreadyExists(entity_name="Application", entity_id=application_input.application_id)

                new_application = Application.from_orm(application_input)
                db.add(new_application)
                db.commit()
                db.refresh(new_application)
                return new_application
        except EntityAlreadyExists:
            raise
        except Exception as e:
            raise DatabaseError(func_name="create_application", detail=str(e))

    @staticmethod
    def update_application(
            db: Session, application_id: str, new_application_data: ApplicationBase
    ) -> Application:
        """
        Update an application in the database.

        :param db: The database session.
        :param application_id: The ID of the application to update.
        :param new_application_data: The new data to update the application with.
        :return: The updated application.
        :raises EntityNotFound: If the application does not exist.
        :raises DatabaseError: If there was an error updating the application.
        """
        try:
            with db:
                db_application = db.exec(select(Application).where(
                    Application.application_id == new_application_data.application_id
                )).first()
                if not db_application:
                    raise EntityNotFound(entity_name="Application", entity_id=application_id)

                application_data = new_application_data.dict(exclude_unset=True)
                for key, value in application_data.items():
                    setattr(db_application, key, value)
                db.commit()
                db.refresh(db_application)
                return db_application
        except EntityNotFound:
            raise
        except Exception as e:
            raise DatabaseError(func_name="update_application", detail=str(e))

    @staticmethod
    def read_application(db: Session, application_id: str) -> Application:
        """
        Get an application from the database.

        :param db: The database session.
        :param application_id: The ID of the application to get.
        :return: The retrieved application.
        :raises EntityNotFound: If the application does not exist.
        :raises DatabaseError: If there was an error retrieving the application.
        """
        try:
            with db:
                db_application = db.exec(
                    select(Application).where(Application.application_id == application_id)).first()
                if not db_application:
                    raise EntityNotFound(entity_name="Application", entity_id=application_id)
                return db_application
        except EntityNotFound:
            raise
        except Exception as e:
            raise DatabaseError(func_name="read_application", detail=str(e))

    @staticmethod
    def delete_application(db: Session, application_id: str):
        """
        Delete an application from the database.

        :param db: The database session.
        :param application_id: The ID of the application to delete.
        :raises EntityNotFound: If the application does not exist.
        :raises DatabaseError: If there was an error deleting the application.
        """
        try:
            with db:
                application = db.exec(select(Application).where(Application.application_id == application_id)).first()
                if not application:
                    raise EntityNotFound(entity_name="Application", entity_id=application_id)

                db.delete(application)
                db.commit()
        except Exception as e:
            raise DatabaseError(func_name="delete_application", detail=str(e))

    @staticmethod
    def list_application(db: Session) -> List[ApplicationRead]:
        """
        Get a list of all applications in the database.

        :param db: The database session.
        :return: A list of all applications in the database.
        :raises DatabaseError: If there was an error retrieving the applications.
        """
        try:
            applications = db.query(Application).all()
            return [ApplicationRead.from_orm(application) for application in applications]
        except Exception as e:
            raise DatabaseError(func_name="list_application", detail=str(e))
