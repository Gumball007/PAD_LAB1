from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from starlette import status
import httpx

from food_ordering.app.api.db.session import get_db
from food_ordering.app.api import schemas
from food_ordering.app.api.db import models

orders = APIRouter()


@orders.post("/orders", response_model=schemas.PlaceOrderResponse)
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
    # httpx.post("http://localhost:8000/callback/restaurants/orders", json=jsonable_encoder(request))

    return schemas.PlaceOrderResponse(order_id=order_request.id, restaurant_id=payload.restaurant_id,
                                      message="Order placed")


@orders.get("/orders/{order_id}")
async def track_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No order with this id: {order_id} found")

    return order


@orders.post("/callback/orders/{order_id}/complete", response_model=schemas.CallbackResponse)
async def order_completion_callback(order_id: int, callback_data: schemas.CallbackRequest, db: Session = Depends(get_db)):
    order = db.query(models.Order).get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No order with this id: {id} found")
    order.status = "Done"
    db.add(order)
    db.commit()
    db.refresh(order)

    return callback_data


@orders.get("/status", status_code=200)
async def get_status():
    return {"status": "OK"}
