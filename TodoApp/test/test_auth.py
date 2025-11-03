# pylint: disable=W0613, W0621, F6401
"""Tests for auth module"""

from test import utils as t_utils
from datetime import timedelta
from jose import jwt
import pytest
from sqlalchemy import text
from fastapi import HTTPException
from routers.auth import (
    get_db,
    authenticate_user,
    bcrypt_context,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
    get_current_user,
)
from main import app
from models import Users


@pytest.fixture
def test_user():
    """fixture to create a user fro testing purposes

    Yields:
        user: A user model instance
    """
    user = Users(
        username="el_gfe",
        email="es_el_gfe@gmail.com",
        first_name="El",
        last_name="Gfe",
        hashed_password=bcrypt_context.hash("testpassword"),
        role="admin",
        phone_number="(777)-777-7777",
    )

    db = t_utils.TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user

    with t_utils.engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()


app.dependency_overrides[get_db] = t_utils.override_get_db


def test_authenticate_user(test_user):
    """Test you can auth a user"""
    db = t_utils.TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, "testpassword", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username


def test_authenticate_user_wrong_user(test_user):
    """Test you fail an inexisting user"""
    db = t_utils.TestingSessionLocal()

    non_existing_user = authenticate_user("WRONG", "testpassword", db)
    assert non_existing_user is False


def test_create_access_token():
    """Test for token creation"""
    username = "testuser"
    user_id = 1
    role = "user"
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)

    decoded_token = jwt.decode(
        token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False}
    )
    assert decoded_token["sub"] == username
    assert decoded_token["id"] == user_id
    assert decoded_token["role"] == role


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    """Test token get async"""
    encode = {"sub": "testuser", "id": 1, "role": "admin"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {"username": "testuser", "id": 1, "user_role": "admin"}


@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    """Test for an authenticating user with no payload in request"""
    encode = {"role": "user"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Who are you, m8?"
