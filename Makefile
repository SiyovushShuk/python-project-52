.PHONY: install migrate collectstatic setup build render-start dev-server lint

install:
	uv sync

migrate:
	uv run python manage.py migrate

collectstatic:
	uv run python manage.py collectstatic --noinput

setup: install migrate collectstatic

build:
	./build.sh

render-start:
	uv run gunicorn task_manager.wsgi

dev-server:
	uv run python manage.py runserver 0.0.0.0:8000

lint:
	uv run ruff check .
