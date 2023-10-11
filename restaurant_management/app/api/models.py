from pydantic import BaseModel

# defining the request and response models using Pydantic
class RestaurantListResponse(BaseModel):
    id: int
    name: str

class MenuResponseItem(BaseModel):
    id: str
    name: str
    price: float

class RestaurantMenuResponse(BaseModel):
    name: str
    menu: list[MenuResponseItem]

class MenuRequest(BaseModel):
    name: str
    description: str
    price: float

class MenuResponse(BaseModel):
    item_id: str
    name: str
    description: str
    price: float

class OrderCallbackRequest(BaseModel):
    restaurant_id: int
    order_id: int
    status: str

class OrderCallbackResponse(BaseModel):
    restaurant_id: int
    order_id: int
    status: str
