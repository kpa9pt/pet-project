import pytest
from unittest.mock import AsyncMock, MagicMock
from services.order_processor.app.repository import OrderRepository

# @pytest.mark.asyncio


class TestOrderRepository:
    @pytest.mark.asyncio
    async def test_create_success(self):
        # 1. Создаём фейковую сессию
        fake_session = MagicMock()
        fake_session.add = MagicMock()
        fake_session.commit = AsyncMock()
        fake_session.refresh = AsyncMock()

        # 2. Создаём репозиторий с фейковой сессией
        repo = OrderRepository(fake_session)

        # 3. Вызываем метод create
        order = await repo.create("Пицца", 2, 123)

        # 4. Проверяем, что сессия получила правильные вызовы
        fake_session.add.assert_called_once()
        fake_session.commit.assert_awaited_once()
        fake_session.refresh.assert_awaited_once()

        # 5. Проверяем поля заказа
        assert order.product_name == "Пицца"  # здесь заказ возвращается из refresh

    @pytest.mark.asyncio
    async def test_get_by_user_with_orders(self):
        # 1. Создаём фейковую сессию. AsyncMock, потому что есть await session.execute()
        fake_session = AsyncMock()

        # 2. Создаём фейковый заказ, который должен вернуться из БД
        fake_order = MagicMock()
        fake_order.id = 1
        fake_order.product_name = "Пицца"

        # 3. Создаём "фейковый результат", который будет вести себя как объект Result
        mock_result = MagicMock()

        # 4. Настраиваем цепочку: result.scalars().all() → [fake_order]
        #    scalars() → вернуть объект, у которого есть all()
        #    all() → вернуть список [fake_order]
        mock_result.scalars.return_value.all.return_value = [fake_order]

        # 5. Говорим: при вызове session.execute() верни mock_result
        fake_session.execute.return_value = mock_result

        repo = OrderRepository(fake_session)
        orders = await repo.get_by_user(123)

        # 6. Проверяем
        assert len(orders) == 1
        assert orders[0].product_name == "Пицца"

    @pytest.mark.asyncio
    async def test_get_by_user_empty(self):
        fake_session = AsyncMock()

        mock_result = MagicMock()
        # Единственное отличие: .all() возвращает пустой список
        mock_result.scalars.return_value.all.return_value = []

        fake_session.execute.return_value = mock_result

        repo = OrderRepository(fake_session)
        orders = await repo.get_by_user(999)

        assert orders == []
