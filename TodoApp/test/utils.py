""" Utilities for tests
"""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app
from .testing_env import TEST_DATABASE_URL

SQLALCHEMY_DATABASE_URL = TEST_DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    """overr

    Yields:
        _type_: db session obj
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    """ a mocked user for testing purposes

    Returns:
        dict: a user dict
    """
    return {"username": "ambrosio", "id": 1, "user_role": "admin"}

client = TestClient(app)
