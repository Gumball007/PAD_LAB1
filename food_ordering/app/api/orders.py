import time

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette import status
import httpx
from starlette.responses import JSONResponse
from itertools import cycle
from sqlalchemy import text

from app.api.db.session import get_db
from app.api import schemas
from app.api.db import models

orders = APIRouter()

# In-memory storage for request counters
request_counters = {}
#
ports = ["http://restaurantmanagement-1:9000",
         "http://restaurantmanagement-2:9001",
         "http://restaurantmanagement-3:9002",
         "http://restaurantmanagement-4:9003"]
#
# ports = ["http://localhost:9000"]

round_robin = cycle(ports)


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


@orders.post("/orders", dependencies=[Depends(RateLimiter(requests_limit=3, time_window=60))])
async def place_order(payload: schemas.PlaceOrderRequest, db: Session = Depends(get_db)):
    order_request = models.Order(customer_id=payload.customer_id, restaurant_id=payload.restaurant_id,
                                 status="In-Progress")
    db.add(order_request)
    db.commit()
    db.refresh(order_request)

    for item in payload.items:
        new_order_item = models.OrderItem(order_id=order_request.id, item_id=item.item_id, quantity=item.quantity)
        db.add(new_order_item)
        db.commit()
        db.refresh(new_order_item)

    request = schemas.OrderCallbackRequest(restaurant_id=payload.restaurant_id, order_id=order_request.id,
                                           status="In-Progress")

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{next(round_robin)}/callback/restaurants/orders",
                              json=jsonable_encoder(request))

        if r.status_code != 200:
            order_request.status = "Declined"
            db.add(order_request)
            db.commit()
            db.refresh(order_request)

            return JSONResponse(status_code=r.status_code, content=r.json())

        else:
            return schemas.PlaceOrderResponse(order_id=order_request.id, restaurant_id=payload.restaurant_id,
                                              message="Order placed")


@orders.get("/orders/{order_id}", dependencies=[Depends(RateLimiter(requests_limit=3, time_window=60))])
async def track_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No order with this id: {order_id} found")

    return order


@orders.get("/orders/{order_id}/items", response_model=list[dict],
            dependencies=[Depends(RateLimiter(requests_limit=3, time_window=60))])
async def get_ordered_items(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).get(order_id)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with this id: {order_id} found")

    items = db.query(models.OrderItem.item_id, models.OrderItem.quantity).filter(
        models.OrderItem.order_id == order_id).all()

    item_details = []
    for item_id, quantity in items:
        item_details.append({
            "item_id": item_id,
            "quantity": quantity
        })

    return item_details


@orders.get("/status", status_code=200)
async def get_status():
    return {"status": "OK"}


@orders.get("/health", status_code=200)
async def get_status(db: Session = Depends(get_db)):
    try:
        db.execute(text('SELECT 1'))
        return {"status": "OK"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database is down")
