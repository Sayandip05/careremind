.PHONY: dev test migrate shell admin logs build clean

dev:
	docker-compose up

test:
	docker-compose exec fastapi pytest
	docker-compose exec django python manage.py test

migrate:
	docker-compose exec fastapi alembic upgrade head
	docker-compose exec django python manage.py migrate

shell:
	docker-compose exec fastapi python -c "from app.core.database import get_db; print('FastAPI shell')"

admin:
	docker-compose exec django python manage.py shell

logs:
	docker-compose logs -f

build:
	docker-compose build

clean:
	docker-compose down -v
