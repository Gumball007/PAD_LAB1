from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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


@restaurants.post("/callback/restaurants/orders", response_model=schemas.OrderCallbackResponse)
async def order_completion_callback(payload: schemas.OrderCallbackRequest):
    return payload


@restaurants.get("/status", status_code=200)
async def get_status():
    return {"status": "OK"}
