from sqlmodel import select, Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone
from functools import lru_cache

import boto3, os


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def get_or_create(session: Session, model, defaults: dict | None = None, **lookup):
    instance = session.exec(select(model).filter_by(**lookup)).one_or_none()
    if instance:
        return instance, False

    instance = model(**lookup, **(defaults or {}))
    session.add(instance)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()  # another request inserted it first
        instance = session.exec(select(model).filter_by(**lookup)).one()
        return instance, False

    session.refresh(instance)
    return instance, True


@lru_cache
def get_sqs_client():
    return boto3.client("sqs", region_name=os.getenv("AWS_REGION"))
