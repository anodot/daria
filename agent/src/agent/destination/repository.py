from agent.destination import HttpDestination, AuthenticationToken
from agent.modules.db import Session


def exists() -> bool:
    return Session.query(
        Session.query(HttpDestination).exists()
    ).scalar()


def get() -> HttpDestination:
    destination_ = Session.query(HttpDestination).first()
    if not destination_:
        raise DestinationNotExists(f"Destination does not exist")
    return destination_


def save(destination_: HttpDestination):
    if not Session.object_session(destination_):
        Session.add(destination_)
    Session.commit()


def delete():
    if not exists():
        return
    Session.delete(get())
    Session.commit()


def save_auth_token(token: AuthenticationToken):
    if not Session.object_session(token):
        Session.add(token)
    Session.commit()


class DestinationNotExists(Exception):
    pass
