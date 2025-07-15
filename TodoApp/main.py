from typing import Annotated
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
from models import Todos
from database import SessionLocal, engine
from routers import auth

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()