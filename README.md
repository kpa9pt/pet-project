# Order Processing System

Микросервисная система обработки заказов. Принимает заказы через HTTP, обрабатывает через gRPC, отправляет уведомления в Telegram через RabbitMQ.

## Архитектура

- **Gateway (FastAPI)** — HTTP вход, JWT авторизация, gRPC клиент
- **Order Processor (gRPC)** — бизнес-логика заказов, хранение в PostgreSQL
- **Notifier (Telegram bot)** — подписчик на RabbitMQ, отправка уведомлений

## Запуск

```bash
docker-compose up --build