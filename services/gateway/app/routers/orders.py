import grpc
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from services.gateway.app import (
    get_current_user,
    get_grpc_stub,
    OrderRequest,
    OrderResponse,
    OrderListItem,
)
from shared import Order, order_pb2, order_pb2_grpc
from ..rabbit.producer import publish_order_notification
from services.gateway.app.dependencies import grpc_circuit_breaker
from shared.db import get_async_session_maker

router = APIRouter(prefix="/orders", tags=["orders"])

session_maker = get_async_session_maker()


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_req: OrderRequest,
    user_id: int = Depends(get_current_user),
    stub: order_pb2_grpc.OrderProcessorStub = Depends(get_grpc_stub),
):
    if user_id != order_req.user_id:
        raise HTTPException(status_code=403, detail="user_id mismatch")

    grpc_request = order_pb2.OrderRequest(
        product_name=order_req.product_name,
        quantity=order_req.quantity,
        user_id=order_req.user_id,
    )

    try:
        grpc_response = await grpc_circuit_breaker.call(stub.CreateOrder, grpc_request)
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
    except Exception as e:
        if "Circuit Breaker" in str(e):
            raise HTTPException(
                status_code=503, detail="Сервис временно недоступен, попробуйте позже"
            )
        raise HTTPException(status_code=500, detail=str(e))

    # Отправляем уведомление в RabbitMQ
    await publish_order_notification(
        grpc_response.order_id,
        order_req.product_name,
        order_req.quantity,
        order_req.user_id,
    )

    return OrderResponse(
        order_id=grpc_response.order_id,
        status=grpc_response.status,
        message=grpc_response.message,
    )


@router.get("/", response_model=list[OrderListItem])
async def get_orders(user_id: int = Depends(get_current_user)):
    async with session_maker() as session:
        result = await session.execute(select(Order).where(Order.user_id == user_id))
        orders = result.scalars().all()
        return [
            OrderListItem(
                order_id=o.id,
                product_name=o.product_name,
                quantity=o.quantity,
                status=o.status,
                created_at=o.created_at.isoformat(),
            )
            for o in orders
        ]
