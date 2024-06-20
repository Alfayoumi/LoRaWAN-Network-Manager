import os

from sqlmodel import SQLModel
from sqlmodel import Session
from sqlmodel import create_engine
import kpi_calculation.database.models


# The URL of the PostgreSQL database to connect to
POSTGRES_URL = os.getenv("POSTGRES_URL")

# Create a new engine with the given database URL
db_engine = create_engine(POSTGRES_URL, echo=True)


def create_db_and_tables(engine) -> None:
    """
    Create the database and tables defined in the SQLModel metadata.
    """
    # Create all tables defined in the SQLModel metadata
    SQLModel.metadata.create_all(engine)


def drop_db_and_tables(engine) -> None:
    """
    Drop the database and tables defined in the SQLModel metadata.
    """
    # Drop all tables defined in the SQLModel metadata
    SQLModel.metadata.drop_all(engine)


def get_session() -> Session:
    """
    Return a new database session for interacting with the database.
    """
    # Open a new database session with the engine and yield it to the caller
    with Session(db_engine) as session:
        yield session
