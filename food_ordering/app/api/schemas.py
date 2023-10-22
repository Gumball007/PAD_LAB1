from typing import List
from pydantic import BaseModel


# defining the request and response models using Pydantic
class OrderItem(BaseModel):
    item_id: int
    quantity: int


class PlaceOrderRequest(BaseModel):
    customer_id: int
    restaurant_id: int
    items: List[OrderItem]


class PlaceOrderResponse(BaseModel):
    order_id: int
    restaurant_id: int
    message: str


class TrackOrderResponse(BaseModel):
    order_id: int
    status: str
    items: List[OrderItem]


class CallbackRequest(BaseModel):
    order_id: int
    status: str
    message: str


class OrderCallbackRequest(BaseModel):
    restaurant_id: int
    order_id: int
    status: str
