import os
from sqlmodel import SQLModel, Session, create_engine
from fastapi import Depends
from typing import Annotated
from config import URL_DATABASE

engine = create_engine(URL_DATABASE, echo=True,)


def create_db_and_tables():
    """Creates tables in the chosen database."""
    SQLModel.metadata.create_all(engine)


create_db_and_tables()


def get_session():
    """Yields a session from the selected database engine."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
