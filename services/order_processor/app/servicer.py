from shared import async_session_maker, order_pb2, order_pb2_grpc
from .repository import OrderRepository


class OrderProcessorServicer(order_pb2_grpc.OrderProcessorServicer):
    """gRPC сервер для обработки заказов."""

    async def CreateOrder(self, request, context):
        """
        Создать новый заказ.
        Вызывается при получении gRPC запроса CreateOrder.
        """
        # 1. Создаём сессию БД (асинхронный контекстный менеджер)
        async with async_session_maker() as session:
            # 2. Создаём репозиторий (внедряем сессию через конструктор)
            repo = OrderRepository(session)

            # 3. Вызываем метод репозитория (вся работа с БД скрыта внутри)
            order = await repo.create(
                product_name=request.product_name,
                quantity=request.quantity,
                user_id=request.user_id,
            )

            # 4. Формируем gRPC ответ
            return order_pb2.OrderReply(
                order_id=order.id,
                status=order.status,
                message=f"Заказ на {order.product_name} принят",
            )
