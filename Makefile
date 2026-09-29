.PHONY: build setup install migrate collectstatic render-start dev-server lint test test-coverage

build: setup
	@true

setup: install migrate collectstatic

install:
	uv sync

migrate: install
	uv run python manage.py migrate

collectstatic: install
	uv run python manage.py collectstatic --noinput

render-start:
	uv run gunicorn task_manager.wsgi

dev-server:
	uv run python manage.py runserver 0.0.0.0:8000

lint:
	uv run ruff check .

test:
	uv run python manage.py test users.tests statuses.tests labels.tests tasks.tests

test-coverage:
	uv run coverage run manage.py test users.tests statuses.tests labels.tests tasks.tests
	uv run coverage report
	uv run coverage xml
	uv run python make_coverage_badge.py
