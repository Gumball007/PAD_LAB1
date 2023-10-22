import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from restaurant_management.app.api.db import models
from restaurant_management.app.api.db.session import get_db
from restaurant_management.app.api import schemas

restaurants = APIRouter()


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


@restaurants.get("/restaurants", response_model=list[schemas.RestaurantResponse])
async def browse_restaurants(db: Session = Depends(get_db)):
    restaurants_entries = db.query(models.Restaurant).all()
    return restaurants_entries


@restaurants.get("/restaurants/{restaurant_id}")
async def browse_menus(restaurant_id: int, db: Session = Depends(get_db)):
    return get_restaurant_menu(restaurant_id, db)


@restaurants.post("/callback/restaurants/orders")
async def order_completion_callback(payload: schemas.CallbackRequest, db: Session = Depends(get_db)):
    restaurant = db.query(models.Restaurant).get(payload.restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No restaurant with this id: {id} found")

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
