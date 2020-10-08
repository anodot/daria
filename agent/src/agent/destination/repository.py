from agent.destination import HttpDestination, AuthenticationToken
from agent.modules.db import session


def exists() -> bool:
    return session().query(
        session().query(HttpDestination).exists()
    ).scalar()


def get() -> HttpDestination:
    destination_ = session().query(HttpDestination).first()
    if not destination_:
        raise DestinationNotExists(f"Destination does not exist")
    return destination_


def save(destination_: HttpDestination):
    session().add(destination_)
    session().commit()


def delete():
    if not exists():
        return
    session().delete(get())
    session().commit()


def save_auth_token(token: AuthenticationToken):
    session().add(token)
    session().commit()


class DestinationNotExists(Exception):
    pass
