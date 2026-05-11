import pytest
from services.order_processor.app.repository import OrderRepository


@pytest.mark.asyncio
async def test_fastapi_create_order_integration(client, db_session):
    response = client.post(
        "/orders/",
        json={
            "product_name": "Пицца Маргарита",
            "quantity": 2,
            "user_id": 1,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] > 0

    repo = OrderRepository(db_session)
    order = await repo.get_by_id(data["order_id"])
    assert order is not None
    assert order.product_name == "Пицца Маргарита"
