from fastapi import Depends

from sqlmodel import Session, create_engine
from sqlalchemy import JSON, URL

from typing import Annotated
import os

DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["DATABASE_USER"],
    password=os.environ["DATABASE_PASSWORD"],
    host=os.environ["DATABASE_HOST"],
    port=int(os.environ.get("DATABASE_PORT", 5432)),
    database=os.environ["DATABASE_NAME"],
)
engine = create_engine(DATABASE_URL, echo=False)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
