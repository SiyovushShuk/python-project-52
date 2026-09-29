### Hexlet tests and linter status:
[![Actions Status](https://github.com/SiyovushShuk/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/SiyovushShuk/python-project-52/actions)
[![CI: Lint + Tests + Coverage](https://github.com/SiyovushShuk/python-project-52/actions/workflows/ci.yml/badge.svg)](https://github.com/SiyovushShuk/python-project-52/actions)

# Task Manager

Task Manager — система управления задачами, подобная Redmine. В ней можно ставить задачи, назначать исполнителей, менять статусы задач, помечать их метками и фильтровать список по любому из этих признаков.

## Деплой

Приложение задеплоено и доступно по адресу:

🔗 **[task-manager-ckak.onrender.com](https://task-manager-ckak.onrender.com)**

## Технологии

- **Python 3.10+** и пакетный менеджер **uv**
- **Django** — ORM, шаблонизатор DjangoTemplates, формы, аутентификация и авторизация
- **PostgreSQL** в продакшене (psycopg2-binary, dj-database-url), **SQLite** — для локальной разработки
- **django-filter** — фильтрация списка задач
- **Bootstrap 5** через CDN — UI, серверный рендер шаблонов DjangoTemplates
- **render.com** — PaaS для деплоя, приложение запускается через **gunicorn**
- **python-dotenv** — настройки и секреты через переменные окружения
- **Ruff** — линтер

## Локальный запуск

### Предварительные требования

- Python 3.10 или выше
- uv

### Установка и запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/SiyovushShuk/python-project-52.git
   cd python-project-52
   ```

2. Создайте файл `.env` на основе `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Отредактируйте `.env` и укажите свои значения переменных окружения.

3. Установите зависимости, примените миграции и соберите статику:
   ```bash
   make setup
   ```

4. Запустите сервер разработки:
   ```bash
   make dev-server
   ```

   Приложение будет доступно по адресу http://localhost:8000

## Команды Makefile

- `make install` — установить зависимости с помощью uv
- `make migrate` — применить миграции базы данных
- `make collectstatic` — собрать статические файлы
- `make setup` — полная настройка окружения (install + migrate + collectstatic)
- `make build` — запустить скрипт сборки для деплоя (build.sh)
- `make render-start` — запустить приложение через gunicorn (для render.com)
- `make dev-server` — запустить сервер разработки Django
- `make lint` — запустить линтер Ruff
- `make test` — запустить тесты Django
- `make test-coverage` — запустить тесты с отчетом о покрытии (порог 70%)

## Деплой на Render.com

1. Создайте аккаунт на [render.com](https://render.com)
2. Создайте новый **Web Service** и подключите свой репозиторий
3. В настройках сервиса укажите:
   - **Build Command**: `make build`
   - **Start Command**: `make render-start`
4. В разделе **Environment** добавьте переменные окружения:
   - `SECRET_KEY` — секретный ключ Django (сгенерируйте сложную случайную строку)
   - `DEBUG` — `False` для продакшена
   - `DATABASE_URL` — URL для подключения к PostgreSQL (создастся автоматически при добавлении сервиса базы данных)
5. Добавьте сервис базы данных **PostgreSQL** и подключите его к вашему Web Service
6. Нажмите **Create Web Service**

После успешного деплоя приложение будет доступно по домену, предоставленному Render.com.
