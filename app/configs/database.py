# db connection related stuff
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

from .env import settings

# Create Database Engine
connect_args = {"check_same_thread": False}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
