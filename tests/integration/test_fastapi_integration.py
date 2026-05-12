import pytest
import requests
from shared.db.session import get_async_session_maker
from services.order_processor.app.repository import OrderRepository


@pytest.mark.asyncio
async def test_fastapi_create_order_integration(db_session):
    # 1. Получаем токен через реальный эндпоинт
    login_response = requests.post(
        "http://localhost:8000/auth/login", json={"user_id": 1}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 2. Создаём заказ
    response = requests.post(
        "http://localhost:8000/orders/",
        json={"product_name": "Пицца Маргарита", "quantity": 2, "user_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] > 0

    # 3. Проверяем в БД
    async_session_maker = get_async_session_maker()
    async with async_session_maker() as session:
        repo = OrderRepository(session)
        order = await repo.get_by_id(data["order_id"])
        assert order is not None
        assert order.product_name == "Пицца Маргарита"
