import os
from faststream.rabbit import RabbitBroker

broker = RabbitBroker(host=os.getenv("RABBITMQ_HOST", "localhost"))
