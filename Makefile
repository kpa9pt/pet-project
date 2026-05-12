up:
	docker compose up -d --build

down:
	docker compose down -v

test:
	./scripts/test.sh
