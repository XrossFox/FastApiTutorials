# pylint: disable=W0613, W0621
"""Tests for user module
"""

import test.utils as t_utils
import pytest
from fastapi import status
from sqlalchemy import text
from routers.users import get_db, get_current_user
from routers.auth import bcrypt_context
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
        phone_number="(777)-777-7777"
    )

    db = t_utils.TestingSessionLocal()
    db.add(user)
    db.commit()

    yield user

    with t_utils.engine.connect() as connection:
        connection.execute(text("DELETE FROM users"))
        connection.commit()

app.dependency_overrides[get_db] = t_utils.override_get_db
app.dependency_overrides[get_current_user] = t_utils.override_get_current_user

def test_return_user(test_user):
    """ Test you can retrieve a user
    """
    response = t_utils.client.get("/users/my_profile")
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_json["username"] == "el_gfe"
    assert response_json["email"] == "es_el_gfe@gmail.com"
    assert response_json["first_name"] == "El"
    assert response_json["last_name"] == "Gfe"
    assert response_json["role"] == "admin"
    assert response_json["phone_number"] == "(777)-777-7777"

def test_change_password_success(test_user):
    """ Tests change password happy path
    """
    response = t_utils.client.post("/users/change_password",
                                  json={
                                      "old_password": "testpassword",
                                      "new_password": "newpassword"
                                  })
    assert response.status_code == status.HTTP_201_CREATED

def test_change_password_invalid_current_password(test_user):
    """ Tests change password when an invalid password is used
    """
    response = t_utils.client.post("/users/change_password",
                                   json={
                                       "old_password": "wrong_password",
                                       "new_password": "newpassword",
                                   })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Old Password does not match"}

def test_change_phone_number_success(test_user):
    """ Test you can change your phone number
    """
    response = t_utils.client.put("users/update_phone_number",
                                json={
                                    "new_phone_number": "439300078"
                                })
    assert response.status_code == status.HTTP_204_NO_CONTENT
