import grpc
from shared.grpc_generated import order_pb2_grpc

from .circuit_breaker import CircuitBreaker

# Создаём один экземпляр на всё приложение
grpc_circuit_breaker = CircuitBreaker(failure_threshold=2, timeout=10)


async def get_grpc_stub():
    """Создаёт и возвращает gRPC stub для OrderProcessor."""
    channel = grpc.aio.insecure_channel("localhost:50051")
    stub = order_pb2_grpc.OrderProcessorStub(channel)
    try:
        yield stub
    finally:
        await channel.close()
