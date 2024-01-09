from sqlalchemy import create_engine
import os

def db_credentials():
    # define the db connection credentials, taken from .env
    db_params = {
        'user': os.environ['USER'],
        'password': os.environ['PASSWORD'],
        'host': os.environ['HOST'],
        'database': os.environ['DATABASE'],
        'port': os.environ['PORT']
    }
    return db_params


def connect_sqla():
    # try to create connection engine to the db using sqlalchemy
    db_params = db_credentials()
    try:
        engine = create_engine(f'postgresql://{db_params["user"]}:{db_params["password"]}@{db_params["host"]}:{db_params["port"]}/{db_params["database"]}')
        return engine
    except Exception as e:
        print("db connection problem")
    
