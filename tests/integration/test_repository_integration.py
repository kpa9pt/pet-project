import pytest

from services.order_processor.app.repository import OrderRepository


@pytest.mark.asyncio
async def test_create_order(db_session):
    repo = OrderRepository(db_session)

    order = await repo.create(
        product_name="iPhone 15",
        quantity=2,
        user_id=1,
    )

    assert order.id is not None
    assert order.product_name == "iPhone 15"
    assert order.quantity == 2
    assert order.user_id == 1
