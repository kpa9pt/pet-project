"""
Репозиторий для работы с заказами в базе данных.

Слой абстракции между бизнес-логикой (servicer.py) и конкретной реализацией БД.
Если захотим перейти с PostgreSQL на MongoDB — меняем только этот файл.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared import Order


class OrderRepository:
    """
    Репозиторий для операций с заказами.

    Принимает сессию SQLAlchemy в конструкторе (Dependency Injection).
    Это позволяет легко подменять сессию в тестах (например, на фейковую).
    """

    def __init__(self, session: AsyncSession):
        """
        :param session: Асинхронная сессия SQLAlchemy для работы с БД.
        """
        self.session = session

    async def create(self, product_name: str, quantity: int, user_id: int) -> Order:
        """
        Создать новый заказ в базе данных.

        :param product_name: Название товара
        :param quantity: Количество
        :param user_id: ID пользователя (из JWT токена)
        :return: Созданный объект Order (с заполненным id, created_at)
        """
        # 1. Создаём объект ORM модели (пока не сохранён в БД)
        order = Order(
            product_name=product_name,
            quantity=quantity,
            user_id=user_id,
            status="created",  # начальный статус
        )

        # 2. Добавляем объект в сессию (SQLAlchemy начнёт за ним следить)
        self.session.add(order)

        # 3. Сохраняем в БД (фиксируем транзакцию)
        await self.session.commit()

        # 4. Обновляем объект из БД (подгружаем id, created_at и т.д.)
        await self.session.refresh(order)

        return order

    async def get_by_user(self, user_id: int) -> list[Order]:
        """
        Получить все заказы конкретного пользователя.

        :param user_id: ID пользователя
        :return: Список объектов Order (может быть пустым)
        """
        # 1. Формируем SQL запрос через SQLAlchemy Core
        stmt = select(Order).where(Order.user_id == user_id)

        # 2. Выполняем запрос
        result = await self.session.execute(stmt)

        # 3. Извлекаем все строки и преобразуем в объекты Order
        orders = result.scalars().all()

        return orders

    async def get_by_id(self, order_id: int) -> Order | None:
        """
        Получить один заказ по ID.

        :param order_id: ID заказа
        :return: Объект Order или None, если не найден
        """
        stmt = select(Order).where(Order.id == order_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
