import asyncio
import grpc
from services.order_processor.app import OrderProcessorServicer
from shared import order_pb2_grpc


async def serve(stop_event: asyncio.Event = None):
    server = grpc.aio.server()
    order_pb2_grpc.add_OrderProcessorServicer_to_server(
        OrderProcessorServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    print("✅ gRPC сервер запущен на порту 50051")
    await server.start()

    if stop_event:
        await stop_event.wait()
    else:
        await server.wait_for_termination()

    print("🛑 Останавливаем сервер...")
    await server.stop(grace=5)
    print("🛑 gRPC сервер остановлен")


if __name__ == "__main__":
    asyncio.run(serve())
