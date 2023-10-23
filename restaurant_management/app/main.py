import asyncio

from fastapi import FastAPI
from starlette.responses import JSONResponse
from starlette.status import HTTP_408_REQUEST_TIMEOUT

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
REQUEST_TIMEOUT = 3


@app.middleware('http')
async def timeout_middleware(request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=REQUEST_TIMEOUT)
    except asyncio.TimeoutError:
        return JSONResponse({'detail': f'Request exceeded the time limit for processing'},
                            status_code=HTTP_408_REQUEST_TIMEOUT)
