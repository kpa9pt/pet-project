import asyncio
import logging
from aiogram import Bot
from faststream.rabbit import RabbitBroker
from shared import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

bot = Bot(token=settings.telegram_token)
broker = RabbitBroker()

# Куда отправлять уведомления (ваш chat_id, который вы получили раньше)
TELEGRAM_CHAT_ID = 836241714  # замените на свой, если нужно


@broker.subscriber("order")
async def handle_order(data: str):
    """Получает сообщение из очереди и отправляет в Telegram."""
    logger.info(f"Получено сообщение: {data}")
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=data)


async def main():
    async with broker:
        await broker.start()
        logger.info("Notifier запущен, жду сообщения в очереди 'order'")
        await asyncio.Future()  # бесконечное ожидание


if __name__ == "__main__":
    asyncio.run(main())
