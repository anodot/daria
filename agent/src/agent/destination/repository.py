from agent.db import Session
from agent import destination, source, pipeline

session = Session()


def exists() -> bool:
    return session.query(
        session.query(destination.HttpDestination).exists()
    ).scalar()


def get() -> destination.HttpDestination:
    return _get_entity()


def upsert(destination_: destination.HttpDestination):
    update(destination_) if exists() else create(destination_)


def create(destination_: destination.HttpDestination):
    session.add(destination_)
    session.commit()


def update(destination_: destination.HttpDestination):
    destination_entity = _get_entity()
    destination_entity.host_id = destination_.host_id
    destination_entity.access_key = destination_.access_key
    destination_entity.config = destination_.config
    session.commit()


def delete():
    if not exists():
        return
    session.delete(_get_entity())
    session.commit()


def _get_entity() -> destination.HttpDestination:
    destination_entity = session.query(destination.HttpDestination).first()
    if not destination_entity:
        raise DestinationNotExists(f"Destination does not exist")
    return destination_entity


class DestinationNotExists(Exception):
    pass
