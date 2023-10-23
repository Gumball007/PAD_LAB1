import asyncio
import time

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette import status
import httpx
from starlette.responses import JSONResponse

from food_ordering.app.api.db.session import get_db
from food_ordering.app.api import schemas
from food_ordering.app.api.db import models

orders = APIRouter()


@orders.post("/orders")
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

    request = schemas.OrderCallbackRequest(restaurant_id=payload.restaurant_id, order_id=order_request.id, status="In-Progress")

    async with httpx.AsyncClient() as client:
        r = await client.post("http://localhost:9000/callback/restaurants/orders", json=jsonable_encoder(request))

        if r.status_code != 200:
            order_request.status = "Declined"
            db.add(order_request)
            db.commit()
            db.refresh(order_request)

            return JSONResponse(status_code=r.status_code, content=r.json())

        else:
            return schemas.PlaceOrderResponse(order_id=order_request.id, restaurant_id=payload.restaurant_id,
                                              message="Order placed")


@orders.get("/orders/{order_id}")
async def track_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No order with this id: {order_id} found")

    return order


@orders.get("/orders/{order_id}/items", response_model=list[dict])
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
