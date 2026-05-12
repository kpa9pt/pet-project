import pytest
import grpc
from shared import order_pb2, order_pb2_grpc


@pytest.mark.asyncio
async def test_grpc_create_order_integration(db_session):
    # Сервис уже поднят docker-compose фикстурой
    channel = grpc.aio.insecure_channel("localhost:50051")
    stub = order_pb2_grpc.OrderProcessorStub(channel)

    request = order_pb2.OrderRequest(
        product_name="Пицца Маргарита", quantity=2, user_id=123
    )

    response = await stub.CreateOrder(request)

    assert response.order_id > 0
    assert response.status == "created"
    assert "Пицца Маргарита" in response.message

    await channel.close()
