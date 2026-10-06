# Url Shortener API

A production-oriented URL shortener built with FastAPI and React that demonstrates scalable backend design using Snowflake ID generation, Base62 encoding, Redis caching, RabbitMQ event-driven analytics, asynchronous workers, PostgreSQL persistence, and Dockerized deployment.

## Features

- User registration and login with JWT bearer tokens
- Authenticated short URL creation
- Distributed Snowflake ID generation for globally unique URL identifiers
- Base62 encoding of Snowflake IDs to generate compact short URLs
- Optional custom aliases between 3 and 10 characters
- Default link expiration of 5 minutes when `expires_at` is not provided
- Redirects from short codes to original URLs
- Click count tracking
- Redis caching for short-code lookups
- Soft delete and permanent delete support for user-owned URLs
- Background click analytics through RabbitMQ
- GeoIP, user-agent, referrer, browser, OS, device, city, country, and IP analytics
- React dashboard for authentication, short-link creation, link management, and analytics views
- PostgreSQL schema management with Alembic
- Docker Compose setup for frontend, API, analytics worker, PostgreSQL, Redis, and RabbitMQ

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
- React
- Vite
- Tailwind CSS
- Nginx for the production frontend container

## URL Generation Strategy

Every shortened URL is generated in two stages:

1. A globally unique **Snowflake ID** is generated.
2. The numeric Snowflake ID is converted into a compact **Base62** string.

Example:
Snowflake ID
↓
781623419872391234
↓
Base62 Encoding
↓
aZ91Kd

This approach provides:

- Globally unique identifiers
- Chronologically sortable IDs
- No database sequence bottlenecks
- Compact, URL-friendly short codes
- High throughput suitable for distributed systems

Custom aliases bypass Base62 generation while still maintaining uniqueness validation.

## Architecture

![Project Architecture](backend/docs/Architecture.png)

## Architecture Highlights

The application follows a layered architecture:

- API Layer (FastAPI routers)
- Service Layer (business logic)
- Repository Layer (database abstraction)
- PostgreSQL for persistent storage
- Redis for caching and analytics aggregation
- RabbitMQ for asynchronous event processing
- Dedicated analytics workers
- React frontend consuming REST APIs

## Production Features

- Layered architecture
- Async SQLAlchemy ORM
- Repository pattern
- JWT authentication
- Redis caching
- RabbitMQ event-driven architecture
- Snowflake distributed ID generation
- Base62 short-code generation
- Soft delete support
- Background analytics processing
- Dockerized deployment
- Alembic database migrations
- Nginx frontend serving

## Project Structure

```text
.
|-- backend/          # FastAPI application, workers, migrations, and backend Dockerfile
|   |-- analytics/    # Click analytics worker, GeoIP, user-agent parsing, cache updates
|   |-- api/          # FastAPI routers and route handlers
|   |-- core/         # App settings, Redis client, security, exception handlers
|   |-- data/         # Local data files such as GeoLite2-City.mmdb
|   |-- db/           # Async database session and dependencies
|   |-- dependencies/ # Request dependencies, including current-user auth
|   |-- docs/         # Architecture diagram and documentation assets
|   |-- exceptions/   # Domain exceptions
|   |-- mappers/      # Model-to-schema mapping helpers
|   |-- messaging/    # RabbitMQ connection, topology, producer, consumer, event schemas
|   |-- migrations/   # Alembic migration files
|   |-- models/       # SQLAlchemy models
|   |-- repositories/ # Database access layer
|   |-- schemas/      # Pydantic request/response schemas
|   |-- services/     # Business logic
|   |-- utils/        # Utility helpers
|   |-- Dockerfile
|   |-- main.py       # FastAPI application entrypoint
|   `-- alembic.ini   # Alembic configuration
|-- frontend/         # React/Vite frontend application and Nginx image
|-- docker-compose.yaml
`-- requirements.txt  # Python dependencies
```

## Requirements

- Python 3.11 or newer
- PostgreSQL
- Redis
- RabbitMQ
- Node.js 22 or newer for local frontend development
- GeoLite2 City database file at `backend/data/GeoLite2-City.mmdb`

Docker Compose can run the frontend, PostgreSQL, Redis, RabbitMQ, the API, and the analytics worker for you.

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

GEOLITE2_PATH=backend/data/GeoLite2-City.mmdb
FRONTEND_ORIGINS=http://localhost:5173,http://localhost:3000

RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASS=password
RABBITMQ_EXCHANGE=url_clicks
RABBITMQ_QUEUE=url_clicks
RABBITMQ_ROUTING_KEY=click
```

When running with Docker Compose, the compose file supplies container network values for the services and mounts `./backend/data/GeoLite2-City.mmdb` into the API, analytics worker, and flush worker containers.

The frontend uses `frontend/.env` for local development:

```env
VITE_API_URL=http://localhost:8000
```

## Backend Setup

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
cd backend
uvicorn main:app --reload
```

Run the analytics worker in a separate terminal:

```bash
cd backend
python -m analytics.bootstrap
```

Run the analytics flush worker in another terminal:

```bash
cd backend
python -m analytics.flush_worker
```

The API is available at:

```text
http://localhost:8000
```

Interactive API docs are available at:

```text
http://localhost:8000/docs
```

## Frontend Setup

Install frontend dependencies:

```bash
cd frontend
npm install
```

Run the Vite development server:

```bash
npm run dev
```

The frontend is available at:

```text
http://localhost:5173
```

Useful frontend commands:

```bash
npm run lint
npm run build
npm run preview
```

## Docker Compose

Start the full stack:

```bash
docker compose up --build
```

This starts:

- `frontend`: React application served by Nginx on port `3000`
- `url_shortener`: FastAPI application on port `8000`
- `analytics_worker`: RabbitMQ consumer that processes click events
- `flush_worker`: Periodically flushes cached analytics aggregates from Redis to PostgreSQL
- `db`: PostgreSQL on port `5432`
- `redis`: Redis on port `6379`
- `rabbitmq`: RabbitMQ on port `5672` and management UI on port `15672`

Open the application at:

```text
http://localhost:3000
```

The API remains available at:

```text
http://localhost:8000/docs
```

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

1. Client requests GET /urls/{short_code}
2. Redis is checked for the short code.
3. On cache miss, PostgreSQL is queried and Redis is updated.
4. URL validity (expiration and active state) is verified.
5. Click count is incremented.
6. Redirect response (307) is returned.
7. Click metadata is published to RabbitMQ.
8. Analytics worker consumes the event.
9. GeoIP and User-Agent information are extracted.
10. Analytics aggregates are updated in Redis.
11. Periodic flush workers persist aggregated analytics into PostgreSQL.

## Design Decisions

### Snowflake IDs

Each URL receives a globally unique 64-bit Snowflake ID before persistence. Snowflake IDs are:

- Time sortable
- Distributed
- Collision resistant
- Generated without database locks

### Base62 Encoding

Instead of exposing numeric IDs directly, Snowflake IDs are Base62 encoded using:

0-9
A-Z
a-z

This creates compact, URL-safe short codes while preserving uniqueness.

### Redis Cache

Redis caches URL lookups to reduce PostgreSQL load during redirects.

### RabbitMQ

Click events are processed asynchronously so redirect latency remains low.

### Flush Worker

Analytics aggregates are periodically flushed from Redis into PostgreSQL to reduce write amplification.

## Development Notes

- Configuration is loaded from `.env` through `pydantic-settings`.
- URL ownership is enforced for authenticated detail, soft delete, and permanent delete operations.
- Expired or inactive URLs are rejected before redirect/detail responses.
- Redis lookup caching falls back to PostgreSQL if Redis is unavailable.
- Alembic migrations live in `backend/migrations/versions`.

## Future Improvements

- QR code generation
- Link password protection
- Custom domains
- Rate limiting
- Bulk URL shortening
- Link tags and folders
- Team workspaces
- Public analytics pages
- Click fraud detection
- Prometheus and Grafana monitoring
- Kubernetes deployment
- CI/CD pipeline with GitHub Actions
