from fastapi import FastAPI

from food_ordering.app.api.db.models import Base
from food_ordering.app.api.db.session import engine
from food_ordering.app.api.orders import orders


def create_tables():
    Base.metadata.create_all(bind=engine)


def start_application():
    app = FastAPI()
    app.include_router(orders)
    create_tables()
    return app


app = start_application()
