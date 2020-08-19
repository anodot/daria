from agent import destination
from agent.db import Session


def exists() -> bool:
    session = Session()
    res = session.query(
        session.query(destination.HttpDestination).exists()
    ).scalar()
    session.close()
    return res


def get() -> destination.HttpDestination:
    session = Session()
    destination_ = session.query(destination.HttpDestination).first()
    session.close()
    if not destination_:
        raise DestinationNotExists(f"Destination does not exist")
    return destination_


def save(destination_: destination.HttpDestination):
    session = Session()
    session.add(destination_)
    session.commit()
    session.close()


def delete():
    if not exists():
        return
    session = Session()
    session.delete(get())
    session.commit()
    session.close()


class DestinationNotExists(Exception):
    pass
