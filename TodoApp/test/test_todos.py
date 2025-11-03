""" Todos testing modules
"""
from test.utils import override_get_current_user, override_get_db
from test.utils import client, engine, TestingSessionLocal
from fastapi import status
import pytest
from sqlalchemy import text
from main import app
from routers.todos import get_db, get_current_user
from models import Todos


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture
def test_todo():
    """ creates a Todo in db for testing

    It tears down the db at the end

    Yields:
        Todo: a Todo model object
    """
    todo: Todos = Todos(
        title="Some title",
        description="A description",
        priority=5,
        complete=False,
        owner_id=1
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


def test_read_all_authenticated(test_todo):
    """ Test read all todos as auth user
    """
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    for_assert = [{
        "description": "A description",
        "complete": False,
        "title": "Some title",
        "priority": "5",
        "owner_id": 1,
        "id": 1
    }]
    assert response.json() == for_assert

def test_read_one_authenticated(test_todo):
    """ Test read one todo as auth user
    """
    response = client.get("/todo/1")
    assert response.status_code == status.HTTP_200_OK
    for_assert = {
        "description": "A description",
        "complete": False,
        "title": "Some title",
        "priority": "5",
        "owner_id": 1,
        "id": 1
    }
    assert response.json() == for_assert

def test_read_one_authenticated_not_found():
    """ Test read one todo that vcant be found
    """
    response = client.get("/todo/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found."}

def test_create_todo(test_todo):
    """ Test create a Todo
    """
    request_data = {
        "title": "New Todo",
        "description": "New description",
        "priority": 5,
        "complete": False,
    }

    response = client.post("/todo/", json=request_data)
    assert response.status_code == 201

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id==2).first()
    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert int(model.priority) == request_data.get("priority")
    assert model.complete == request_data.get("complete")

def test_update_todo(test_todo):
    """ Test update a todo
    """
    request_data={
        "title": "Changed title of todo",
        "description": "Changed description",
        "priority": 4,
        "complete": True
    }

    response = client.put("/todo/1", json=request_data)
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id==1).first()
    assert model.title == request_data.get("title")
    assert model.description == request_data.get("description")
    assert int(model.priority) == request_data.get("priority")
    assert model.complete == request_data.get("complete")

def test_update_todo_not_found(test_todo):
    """ Test todo is not found
    """
    request_data={
        "title": "Changed title of todo",
        "description": "Changed description",
        "priority": 4,
        "complete": True
    }

    response = client.put("/todo/999", json=request_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}

def test_delete_todo_not_found(test_todo):
    """ Delete a todo that cant be found
    """
    response = client.delete("/todo/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found."}
