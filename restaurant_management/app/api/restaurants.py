from fastapi import APIRouter

from app.api.models import *

restaurants = APIRouter()


@restaurants.get("/restaurants", response_model = RestaurantListResponse)
async def browse_restaurants():
    return {"id": 1, "name": "test"}


@restaurants.get("/restaurants/{restaurant_id}", response_model = RestaurantMenuResponse)
async def browse_menus():
    return {"name": "A", "menu": list}


@restaurants.post("/restaurants/{restaurant_id}", response_model = MenuResponse)
async def add_item(restaurant_id: int, payload: MenuRequest):
    return {"item_id": 1, "name": "dish", "description": "good", "price": 18.90}


@restaurants.put("/restaurants/{restaurant_id}", response_model = MenuResponse)
async def update_item(payload: MenuRequest):
    return {"item_id": 1, "name": "dish", "description": "good", "price": 18.90}


@restaurants.post("/callback/restaurants/orders", response_model = OrderCallbackResponse)
async def order_completion_callback(payload: OrderCallbackRequest):
    return {"restaurant_id": 789, "order_id": 1, "status": "received"}
