from fastapi import APIRouter, HTTPException

from app.api.models import *

orders = APIRouter()

@orders.post("/orders", response_model = PlaceOrderResponse)
async def place_order(payload: PlaceOrderRequest):
    return {"order_id": 1, "message": "test"}


@orders.get("/orders/{order_id}", response_model = TrackOrderResponse)
async def track_order(order_id: int):
    item = {"item_id": 4, "quantity": 4}
    return {"order_id": order_id, "status": "test", "items": list}


@orders.post("/callback/orders/{order_id}/complete", response_model = CallbackResponse)
async def order_completion_callback(order_id: int, callback_data: CallbackRequest):
    # Check if the order_id exists in the "database" (in-memory dictionary)
    # if order_id not in order_db:
    #     raise HTTPException(status_code=404, detail="Order not found")

    # update the order status and message based on the callback data
    # order_info = order_db[order_id]
    # order_info["status"] = callback_data.status
    # order_info["message"] = callback_data.message

    # retrieve the updated order status and message
    # status = order_info["status"]
    # message = order_info["message"]

    return {"order_id": order_id, "status": "test", "message": "message"}

