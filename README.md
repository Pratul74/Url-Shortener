# Url Shortener API

A FastAPI URL shortener API with JWT authentication, custom short codes, expiring links, Redis-backed lookup caching, PostgreSQL persistence, RabbitMQ click events, and asynchronous analytics processing.

## Features

- User registration and login with JWT bearer tokens
- Authenticated short URL creation
- Optional custom aliases between 3 and 10 characters
- Default link expiration of 5 minutes when `expires_at` is not provided
- Redirects from short codes to original URLs
- Click count tracking
- Redis caching for short-code lookups
- Soft delete and permanent delete support for user-owned URLs
- Background click analytics through RabbitMQ
- GeoIP, user-agent, referrer, browser, OS, device, city, country, and IP analytics
- PostgreSQL schema management with Alembic
- Docker Compose setup for API, analytics worker, PostgreSQL, Redis, and RabbitMQ

## Tech Stack

- Python
- FastAPI
- SQLAlchemy async ORM
- Alembic
- PostgreSQL
- Redis
- RabbitMQ
- Pydantic
- JWT authentication with `python-jose`
- Password hashing with `passlib` and `bcrypt`
- GeoLite2 city database for location analytics

## Architecture

![Project Architecture](docs/Architecture.png)

## Project Structure

```text
.
|-- analytics/        # Click analytics worker, GeoIP, user-agent parsing, cache updates
|-- api/              # FastAPI routers and route handlers
|-- core/             # App settings, Redis client, security, exception handlers
|-- data/             # Local data files such as GeoLite2-City.mmdb
|-- db/               # Async database session and dependencies
|-- dependencies/     # Request dependencies, including current-user auth
|-- docs/             # Architecture diagram and documentation assets
|-- exceptions/       # Domain exceptions
|-- mappers/          # Model-to-schema mapping helpers
|-- messaging/        # RabbitMQ connection, topology, producer, consumer, event schemas
|-- migrations/       # Alembic migration files
|-- models/           # SQLAlchemy models
|-- repositories/     # Database access layer
|-- schemas/          # Pydantic request/response schemas
|-- services/         # Business logic
|-- utils/            # Utility helpers
|-- docker-compose.yaml
|-- Dockerfile
|-- main.py           # FastAPI application entrypoint
|-- alembic.ini       # Alembic configuration
`-- requirements.txt  # Python dependencies
```

## Requirements

- Python 3.11 or newer
- PostgreSQL
- Redis
- RabbitMQ
- GeoLite2 City database file at `data/GeoLite2-City.mmdb`

Docker Compose can run PostgreSQL, Redis, RabbitMQ, the API, and the analytics worker for you.

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/url_shortener_db
BASE_URL=http://localhost:8000
SECRET_KEY=replace-with-a-secure-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_CACHE_TTL_SECONDS=86400

GEOLITE2_PATH=data/GeoLite2-City.mmdb

RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASS=password
RABBITMQ_EXCHANGE=url_clicks
RABBITMQ_QUEUE=url_clicks
RABBITMQ_ROUTING_KEY=click
```

When running with Docker Compose, the compose file supplies container network values for the services and mounts `./data/GeoLite2-City.mmdb` into the API and analytics worker containers.

## Setup

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply database migrations:

```bash
alembic upgrade head
```

Run the API:

```bash
uvicorn main:app --reload
```

Run the analytics worker in a separate terminal:

```bash
python -m analytics.bootstrap
```

The API is available at:

```text
http://localhost:8000
```

Interactive API docs are available at:

```text
http://localhost:8000/docs
```

## Docker Compose

Start the full stack:

```bash
docker compose up --build
```

This starts:

- `url_shortener`: FastAPI application on port `8000`
- `analytics_worker`: RabbitMQ consumer that processes click events
- `db`: PostgreSQL on port `5432`
- `redis`: Redis on port `6379`
- `rabbitmq`: RabbitMQ on port `5672` and management UI on port `15672`

## API Overview

### Health Check

```http
GET /
```

Returns a simple API message.

### Register

```http
POST /auth/register
Content-Type: application/json
```

```json
{
  "username": "demo_user",
  "email": "demo@example.com",
  "password": "strongpassword"
}
```

### Login

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
```

```text
username=demo@example.com&password=strongpassword
```

The response includes a bearer token:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### Create a Short URL

```http
POST /urls
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "original_url": "https://example.com/articles/fastapi",
  "custom_alias": "fastapi",
  "expires_at": "2026-12-31T23:59:59Z"
}
```

`custom_alias` and `expires_at` are optional. If `expires_at` is omitted, the link expires after 5 minutes.

### Redirect to Original URL

```http
GET /urls/{short_code}
```

Redirects to the original URL with `307 Temporary Redirect`, increments the URL click count, and publishes a click event for analytics processing.

### List Current User's URLs

```http
GET /urls/get_all
Authorization: Bearer <token>
```

### Get URL Details

```http
GET /urls/detail/{short_code}
Authorization: Bearer <token>
```

### Soft Delete a URL

```http
DELETE /urls/delete/{short_code}
Authorization: Bearer <token>
```

Marks the URL as inactive and removes its cached Redis entry.

### Permanently Delete a URL

```http
DELETE /urls/permanent_delete/{short_code}
Authorization: Bearer <token>
```

Deletes the URL row from the database and removes its cached Redis entry.

### Analytics Dashboard

```http
GET /analytics/{url_id}/dashboard?start_date=2026-01-01&end_date=2026-01-31&target_date=2026-01-15&month=1&year=2026&limit=3
```

Returns click analytics for a URL, including totals, yearly/monthly/daily click counts, top countries, cities, devices, browsers, operating systems, IPs, and grouped click breakdowns.

## Analytics Flow

1. A visitor requests `GET /urls/{short_code}`.
2. The API validates the URL, increments its click count, and redirects the visitor.
3. A background task publishes click metadata to RabbitMQ.
4. The analytics worker consumes the event.
5. The worker enriches the event with GeoIP and user-agent data.
6. The enriched analytics record is stored in PostgreSQL and reflected in Redis analytics cache.

## Development Notes

- Configuration is loaded from `.env` through `pydantic-settings`.
- URL ownership is enforced for authenticated detail, soft delete, and permanent delete operations.
- Expired or inactive URLs are rejected before redirect/detail responses.
- Redis lookup caching falls back to PostgreSQL if Redis is unavailable.
- Alembic migrations live in `migrations/versions`.
