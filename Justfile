up:
    docker compose -f docker/docker-compose.yml up -d

test:
    uv run pytest

start:
    uv run start

down:
    docker compose -f docker/docker-compose.yml down

down-all:
    docker compose -f docker/docker-compose.yml down -v
