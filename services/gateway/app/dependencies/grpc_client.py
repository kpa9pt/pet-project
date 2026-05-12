import grpc
import os
from shared.grpc_generated import order_pb2_grpc

from .circuit_breaker import CircuitBreaker

# Создаём один экземпляр на всё приложение
grpc_circuit_breaker = CircuitBreaker(failure_threshold=2, timeout=10)


async def get_grpc_stub():
    """Создаёт и возвращает gRPC stub для OrderProcessor."""
    grpc_host = os.getenv("GRPC_SERVER_HOST", "localhost")
    grpc_port = os.getenv("GRPC_SERVER_PORT", "50051")
    channel = grpc.aio.insecure_channel(f"{grpc_host}:{grpc_port}")
    stub = order_pb2_grpc.OrderProcessorStub(channel)
    try:
        yield stub
    finally:
        await channel.close()
