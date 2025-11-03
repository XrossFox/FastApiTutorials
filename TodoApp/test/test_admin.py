""" Tests for admin module
"""
from test.utils import override_get_current_user, override_get_db
from test.utils import engine, TestingSessionLocal, client
from fastapi import status
import pytest
from sqlalchemy import text
from routers.admin import get_db, get_current_user
from main import app
from models import Todos


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

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_admin_read_all_authenticated(test_todo):
    """tests admin can read all todos
    """
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    check = [{"complete": False, "title": "Some title",
             "description": "A description", "id": 1,
             "priority": "5", "owner_id": 1}]
    assert response.json() == check

def test_admin_delete_todo(test_todo):
    """ Tests admin can delete todo
    """
    response = client.delete("/admin/todo/1")
    assert response.status_code == 204

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_admin_delete_todo_not_found(test_todo):
    """ Test admin gets 404 when trying to delete a todo
    that doesn't exist
    """
    response = client.delete("/admin/todo/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found."}
