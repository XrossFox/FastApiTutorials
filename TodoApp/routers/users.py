from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from starlette import status
from passlib.context import CryptContext

from models import Users
from .auth import get_current_user

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

router = APIRouter(
    prefix="/users",
    tags=['users']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

@router.get("/my_profile", status_code=status.HTTP_200_OK)
async def get_my_profile(user: user_dependency, db: db_dependency):
    if user is not None:
        actual_query = db.query(Users).filter(Users.id == user.get('id')).first()
        username = actual_query.username
        email = actual_query.email
        first_name = actual_query.first_name
        last_name = actual_query.last_name
        role = actual_query.role
        res = {"username": username, "email": email, "first_name": first_name, "last_name": last_name, "role": role}

        return res
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "U wot m8?")

@router.post("/change_password", status_code=status.HTTP_201_CREATED)
async def change_password(db: db_dependency, user: user_dependency, change_password_request: ChangePasswordRequest):
    if user is not None:
        db_user_data = db.query(Users).filter(Users.id == user.get("id")).first()

        if bcrypt_context.verify(change_password_request.old_password, db_user_data.hashed_password):
            new_hashed_password = bcrypt_context.hash(change_password_request.new_password)
            db.query(Users).filter(Users.id == user.get("id")).update({Users.hashed_password: new_hashed_password})
            db.commit()

        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Old Password does not match")

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Who are ya?")