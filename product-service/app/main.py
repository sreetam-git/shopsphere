from fastapi import FastAPI
from .database import Base, engine
from . import models
from .routers import categories, products, attributes, images
import logging

logging.basicConfig(
    filename="app.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shopsphere Product Service")

app.include_router(categories.router)
app.include_router(products.router)
app.include_router(attributes.router)
app.include_router(images.router)

@app.get("/")
def root():
    return {
        "message": "ShopSphere Product Service is running"
    }