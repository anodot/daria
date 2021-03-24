from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# todo would be nice to have it in the db module
def get_session(connection_string: str):
    return sessionmaker(bind=create_engine(connection_string))()
