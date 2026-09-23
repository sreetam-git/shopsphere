from fastapi import FastAPI
from .database import Base, engine
from . import models
from .routers import users

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ShopSphere User Service")

app.include_router(users.router)

@app.get("/")
def root():
    return {
        "message": "ShopSphere User Service is running"
    }