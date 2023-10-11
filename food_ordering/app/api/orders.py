from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from food_ordering.app.api.db1 import get_db
from schemas import *
from models import *

orders = APIRouter()


@orders.post("/orders", response_model=PlaceOrderResponse)
async def place_order(payload: PlaceOrderRequest, db: Session = Depends(get_db)):
    order_request = Order(customer_id=payload.customer_id, restaurant_id=payload.restaurant_id, status="In-Progress")
    new_order_request_id = order_request.order_id
    db.add(order_request)
    db.commit()

    for item in payload.items:
        new_order_item = OrderItem(order_id=new_order_request_id, item_id=item.item_id, quantity=item.quantity)
        db.add(new_order_item)
        db.commit()

    return PlaceOrderResponse(order_id=new_order_request_id, restaurant_id=payload.restaurant_id,
                              message="Order placed")


@orders.get("/orders/{order_id}")
async def track_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No order with this id: {id} found")

    return order


@orders.post("/callback/orders/{order_id}/complete", response_model=CallbackResponse)
async def order_completion_callback(order_id: int, callback_data: CallbackRequest, db: Session = Depends(get_db)):
    order = db.query(Order).get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No order with this id: {id} found")
    order.status = "Done"
    db.add(order)
    db.commit()

    return callback_data


@orders.get("/status", status_code=200)
async def get_status():
    return {"status": "OK"}
