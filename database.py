from config import URL_DATABASE
from sqlmodel import Session, SQLModel, create_engine
from typing import Annotated
from fastapi import Depends
postgree_url = URL_DATABASE

engine = create_engine(postgree_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
