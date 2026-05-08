from pydantic import BaseModel


class OrderRequest(BaseModel):
    product_name: str
    quantity: int
    user_id: int


class OrderResponse(BaseModel):
    order_id: int
    status: str
    message: str


class OrderListItem(BaseModel):
    order_id: int
    product_name: str
    quantity: int
    status: str
    created_at: str  # или datetime
