import asyncio
import logging

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Простая реализация паттерна Circuit Breaker для защиты вызовов gRPC/HTTP.
    Состояния: CLOSED → OPEN → HALF_OPEN → CLOSED.
    """

    def __init__(self, failure_threshold=3, timeout=5):
        self.failure_threshold = failure_threshold  # сколько ошибок для размыкания
        self.timeout = timeout  # через сколько секунд попробовать снова
        self.failures = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = None

    async def call(self, func, *args, **kwargs):
        """Выполнить функцию с защитой Circuit Breaker."""
        if self.state == "OPEN":
            if asyncio.get_event_loop().time() - self.last_failure_time > self.timeout:
                logger.info("Circuit Breaker переходит в HALF_OPEN")
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit Breaker OPEN: вызов заблокирован")

        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                logger.info("Circuit Breaker переходит в CLOSED")
                self.state = "CLOSED"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
                self.last_failure_time = asyncio.get_event_loop().time()
                logger.error(f"Circuit Breaker OPEN после {self.failures} ошибок")
            raise e
