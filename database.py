import os
from sqlmodel import SQLModel, Session, create_engine
from fastapi import Depends
from typing import Annotated
from config import URL_DATABASE

TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

if TEST_MODE:
    db_url = "sqlite:///:memory:?cache=shared"
    connect_args = {"check_same_thread": False}
else:
    db_url = URL_DATABASE
    connect_args = {}

engine = create_engine(db_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    """Creates tables in the chosen database."""
    SQLModel.metadata.create_all(engine)


create_db_and_tables()


def get_session():
    """Yields a session from the selected database engine."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
