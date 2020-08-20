from agent import destination
from agent.db import Session

session = Session()


def exists() -> bool:
    res = session.query(
        session.query(destination.HttpDestination).exists()
    ).scalar()
    return res


def get() -> destination.HttpDestination:
    destination_ = session.query(destination.HttpDestination).first()
    if not destination_:
        raise DestinationNotExists(f"Destination does not exist")
    return destination_


def save(destination_: destination.HttpDestination):
    session.add(destination_)
    session.commit()


def delete():
    if not exists():
        return
    session.delete(get())
    session.commit()


class DestinationNotExists(Exception):
    pass
