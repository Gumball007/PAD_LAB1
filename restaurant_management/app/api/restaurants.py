from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import *
from restaurant_management.app.api.db2 import get_db
from schemas import *

restaurants = APIRouter()


def menu_query(restaurant_id: int):
    return (
        select(MenuItem, Restaurant)
        .join(Restaurant)
        .where(MenuItem.restaurant_id == restaurant_id)
    )


@restaurants.get("/restaurants", response_model=list[RestaurantResponse])
async def browse_restaurants(db: Session = Depends(get_db)):
    restaurants_entries = db.query(Restaurant).all()
    return restaurants_entries


@restaurants.get("/restaurants/{restaurant_id}", response_model=RestaurantMenuResponse)
async def browse_menus(restaurant_id: int, db: Session = Depends(get_db)):
    results = db.execute(menu_query(restaurant_id))

    menu_items = {
        "name": results.scalar_one().Restaurant.name,
        "menu": [
            {
                "id": str(row.MenuItem.id),
                "name": row.MenuItem.name,
                "price": float(row.MenuItem.price),
            }
            for row in results
        ]
    }

    return menu_items


@restaurants.post("/callback/restaurants/orders", response_model=OrderCallbackResponse)
async def order_completion_callback(payload: OrderCallbackRequest):
    return payload


@restaurants.get("/status", status_code=200)
async def get_status():
    return {"status": "OK"}