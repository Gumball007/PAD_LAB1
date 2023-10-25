import time

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette import status

from app.api.db import models
from app.api.db.session import get_db
from app.api import schemas

restaurants = APIRouter()


# In-memory storage for request counters
request_counters = {}


# Custom RateLimiter class with dynamic rate limiting values per route
class RateLimiter:
    def __init__(self, requests_limit: int, time_window: int):
        self.requests_limit = requests_limit
        self.time_window = time_window

    async def __call__(self, request: Request):
        client_ip = request.client.host
        route_path = request.url.path

        # Get the current timestamp
        current_time = int(time.time())

        # Create a unique key based on client IP and route path
        key = f"{client_ip}:{route_path}"

        # Check if client's request counter exists
        if key not in request_counters:
            request_counters[key] = {"timestamp": current_time, "count": 1}
        else:
            # Check if the time window has elapsed, reset the counter if needed
            if current_time - request_counters[key]["timestamp"] > self.time_window:
                # Reset the counter and update the timestamp
                request_counters[key]["timestamp"] = current_time
                request_counters[key]["count"] = 1
            else:
                # Check if the client has exceeded the request limit
                if request_counters[key]["count"] >= self.requests_limit:
                    raise HTTPException(status_code=429, detail="Too Many Requests")
                else:
                    request_counters[key]["count"] += 1

        # Clean up expired client data (optional)
        for k in list(request_counters.keys()):
            if current_time - request_counters[k]["timestamp"] > self.time_window:
                request_counters.pop(k)

        return True


def get_restaurant_menu(restaurant_id, db: Session):
    restaurant = (
        db.query(models.Restaurant)
        .filter(models.Restaurant.id == restaurant_id)
        .first()
    )

    if not restaurant:
        return None

    menu_items = (
        db.query(models.MenuItem)
        .filter(models.MenuItem.restaurant_id == restaurant_id)
        .all()
    )

    output = {
        "name": restaurant.name,
        "menu": [
            {
                "id": str(menu_item.id),
                "name": menu_item.name,
                "price": menu_item.price
            }
            for menu_item in menu_items
        ]
    }

    return output


@restaurants.get("/restaurants", response_model=list[schemas.RestaurantResponse], dependencies=[Depends(RateLimiter(requests_limit=3, time_window=60))])
async def browse_restaurants(db: Session = Depends(get_db)):
    restaurants_entries = db.query(models.Restaurant).all()
    return restaurants_entries


@restaurants.get("/restaurants/{restaurant_id}", dependencies=[Depends(RateLimiter(requests_limit=3, time_window=60))])
async def browse_menus(restaurant_id: int, db: Session = Depends(get_db)):
    return get_restaurant_menu(restaurant_id, db)


@restaurants.post("/callback/restaurants/orders", dependencies=[Depends(RateLimiter(requests_limit=3, time_window=60))])
async def order_completion_callback(payload: schemas.CallbackRequest, db: Session = Depends(get_db)):
    restaurant = db.query(models.Restaurant).get(payload.restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No restaurant with this id: {payload.restaurant_id} found")

    r = httpx.get(f"http://localhost:8000/orders/{payload.order_id}/items")
    items = r.json()
    print(items)

    for item in items:
        item_id = item["item_id"]

        # Check if an item with the given restaurant_id and item_id exists in the MenuItem table
        item_exists = db.query(models.MenuItem).filter(
            models.MenuItem.id == item_id,
            models.MenuItem.restaurant_id == payload.restaurant_id
        ).first()

        if not item_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"No item with this id: {item_id} found at restaurant with id: {payload.restaurant_id}")

    body = schemas.CallbackRequestResponse(order_id=payload.order_id, status="Done", message="Ready to be picked up!")

    return body


@restaurants.get("/status", status_code=200)
async def get_status():
    return {"status": "OK"}
