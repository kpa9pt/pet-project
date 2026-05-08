from services.gateway.app.rabbit.broker import broker


async def publish_order_notification(
    order_id: int, product_name: str, quantity: int, user_id: int
):
    message = (
        f"Новый заказ #{order_id}: {product_name}, "
        f"{quantity} шт., пользователь {user_id}"
    )
    await broker.publish(message, queue="order")
