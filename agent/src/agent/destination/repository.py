from agent import destination
from agent.db import session


def exists() -> bool:
    return session.query(
        session.query(destination.HttpDestination).exists()
    ).scalar()


def get() -> destination.HttpDestination:
    destination_ = session.query(destination.HttpDestination).first()
    if not destination_:
        raise DestinationNotExists(f"Destination does not exist")
    return destination_


def upsert(destination_: destination.HttpDestination):
    update(destination_) if exists() else create(destination_)


def create(destination_: destination.HttpDestination):
    session.add(destination_)
    session.commit()


def update(destination_: destination.HttpDestination):
    session.add(destination_)
    session.commit()


def delete():
    if not exists():
        return
    session.delete(get())
    session.commit()


class DestinationNotExists(Exception):
    pass
