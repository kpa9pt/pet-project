from contextlib import asynccontextmanager
from fastapi import FastAPI
from services.gateway.app.routers import orders_router, auth_router, health_router
from services.gateway.app.rabbit import broker


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔁 LIFESPAN START: connecting to RabbitMQ...")
    await broker.start()
    print("✅ RabbitMQ connected")
    yield
    print("🔁 LIFESPAN END: closing RabbitMQ...")
    await broker.close()
    print("✅ RabbitMQ closed")


app = FastAPI(title="Order Gateway", lifespan=lifespan)

app.include_router(orders_router)
app.include_router(auth_router)

app.include_router(health_router)
