from agent.db import Session, entity
from agent.destination import HttpDestination

session = Session()


def exists() -> bool:
    return session.query(
        session.query(entity.Destination).exists()
    ).scalar()


def get() -> HttpDestination:
    return HttpDestination.from_entity(_get_entity())


def create(destination_: HttpDestination):
    session.add(destination_.to_entity())
    session.commit()


def update(destination_: HttpDestination):
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


def _get_entity() -> entity.Destination:
    destination_entity = session.query(entity.Destination).first()
    if not destination_entity:
        raise DestinationNotExists(f"Destination does not exist")
    return destination_entity


class DestinationNotExists(Exception):
    pass
