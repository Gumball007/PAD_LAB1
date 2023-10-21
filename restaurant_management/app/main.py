from fastapi import FastAPI

from restaurant_management.app.api.db.models import Base
from restaurant_management.app.api.db.session import engine
from restaurant_management.app.api.restaurants import restaurants


def create_tables():
    Base.metadata.create_all(bind=engine)


def start_application():
    app = FastAPI()
    app.include_router(restaurants)
    create_tables()
    return app


app = start_application()
