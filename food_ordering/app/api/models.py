from pydantic import BaseModel

# defining the request and response models using Pydantic
class OrderItem(BaseModel):
    item_id: int
    quantity: int

class PlaceOrderRequest(BaseModel):
    customer_id: int
    items: list[OrderItem]

class PlaceOrderResponse(BaseModel):
    order_id: int
    message: str

class TrackOrderResponse(BaseModel):
    order_id: int
    status: str
    items: list[OrderItem] 

class CallbackRequest(BaseModel):
    order_id: int
    status: str
    message: str

class CallbackResponse(BaseModel):
    order_id: int
    status: str
    message: str
