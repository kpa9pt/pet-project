import pytest
from shared import async_session_maker
from services.order_processor.app.repository import OrderRepository


@pytest.mark.asyncio
async def test_repository_create_integration(postgres_container):
    async with async_session_maker() as session:
        repo = OrderRepository(session)
        order = await repo.create("Пицца Маргарита", 2, 123)

        assert order.id > 0
        assert order.product_name == "Пицца Маргарита"
        assert order.quantity == 2
        assert order.user_id == 123
        assert order.created_at is not None
