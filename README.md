# Url Shortener API

A FastAPI-based URL shortener with user authentication, custom aliases, expiring links, click tracking, PostgreSQL persistence, Alembic migrations, and Redis configuration support — evolving toward a full Bitly-style link management platform.

## Features

- Register and authenticate users with JWT bearer tokens
- Create short URLs for authenticated users
- Optional custom aliases, from 3 to 10 characters
- Optional expiration timestamps
- Default URL expiration of 5 minutes when no `expires_at` value is provided
- Redirect short codes to their original URLs
- Track click counts
- List, inspect, and deactivate a user's shortened URLs
- PostgreSQL database schema managed with Alembic

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- JWT authentication with `python-jose`
- Password hashing with `passlib` and `bcrypt`

## Current Architecture
![Project Architecture](docs/Architecture.png)

## Project Structure

```text
.
|-- api/              # API routers and route handlers
|-- core/             # App settings, security, Redis, exception handlers
|-- db/               # Database engine, session, and dependencies
|-- dependencies/     # Request dependencies, including current-user auth
|-- exceptions/       # Domain exceptions
|-- mappers/          # Model-to-schema mapping helpers
|-- migrations/       # Alembic migration files
|-- models/           # SQLAlchemy models
|-- repositories/     # Database access layer
|-- schemas/          # Pydantic request/response schemas
|-- services/         # Business logic
|-- utils/            # Utility helpers
|-- main.py           # FastAPI application entrypoint
|-- alembic.ini       # Alembic configuration
`-- requirements.txt  # Python dependencies
```

## Requirements

- Python 3.11 or newer
- PostgreSQL
- Redis

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

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/url_shortener
BASE_URL=http://localhost:8000
SECRET_KEY=replace-with-a-secure-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_CACHE_TTL_SECONDS=86400
```

Apply database migrations:

```bash
alembic upgrade head
```

Run the API:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API docs are available at:

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

Redirects to the original URL with a `307 Temporary Redirect`.

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

### Delete a URL

```http
DELETE /urls/delete/{short_code}
Authorization: Bearer <token>
```

This deactivates the URL instead of physically deleting the database row.

## Development Notes

- Configuration is loaded from `.env` through `pydantic-settings`.
- `DATABASE_URL`, `BASE_URL`, `SECRET_KEY`, `REDIS_HOST`, and `REDIS_PORT` are required.
- URL ownership is enforced for authenticated detail and delete operations.
- Expired or inactive URLs are rejected by the service layer.
- Alembic migrations live in `migrations/versions`.

## Roadmap — Towards a Full Bitly-Like Platform

The current version covers the core shortening/auth/tracking loop. Planned work is grouped below by area.

### 📊 Advanced Analytics
- [ ] Click analytics dashboard: clicks over time, peak hours, daily/weekly/monthly trends
- [ ] Geolocation tracking (country/city) via IP lookup
- [ ] Device, OS, and browser breakdown from user-agent parsing
- [ ] Referrer tracking (which site/social platform sent the click)
- [ ] Unique vs. repeat visitor counts
- [ ] Exportable analytics (CSV/JSON) per link and per account
- [ ] Real-time click stream (WebSocket or SSE) for a live dashboard

### 🔗 Link Management
- [ ] QR code generation for every short link
- [ ] Bulk link creation (CSV/API batch upload)
- [ ] Link editing (retarget a short code to a new destination)
- [ ] Link tags/folders/collections for organization
- [ ] Password-protected links
- [ ] Link preview page (interstitial "you're about to visit..." screen), optional per link
- [ ] UTM parameter builder baked into link creation
- [ ] Deep link / mobile app link support

### 🌐 Custom Domains
- [ ] Bring-your-own-domain support (branded short links)
- [ ] Domain verification (DNS TXT record challenge)
- [ ] Per-domain SSL certificate provisioning (e.g. via Let's Encrypt/ACME)
- [ ] Domain-level default settings (expiration, branding)

### 🏢 Teams & Collaboration
- [ ] Workspaces/organizations with multiple members
- [ ] Role-based access control (owner/admin/member/viewer)
- [ ] Shared link collections within a team
- [ ] Audit log of who created/edited/deleted what

### 🔑 Developer Platform
- [ ] Public REST API with issued API keys (separate from user JWTs)
- [ ] Per-key rate limiting and usage quotas
- [ ] Webhooks for click events and link lifecycle events
- [ ] SDKs/client libraries (Python, JS) for the public API

### 🛡️ Security & Trust
- [ ] Rate limiting on link creation and redirects (e.g. via Redis token bucket / `slowapi`)
- [ ] Malicious/phishing URL scanning before a link goes live (e.g. Google Safe Browsing API integration)
- [ ] CAPTCHA on public/unauthenticated link creation, if that flow is added
- [ ] Configurable link expiration policies (max lifetime, auto-archive)
- [ ] Two-factor authentication for user accounts
- [ ] Refresh tokens and token revocation/blacklisting alongside the existing JWT flow

### ⚙️ Performance & Infrastructure
- [ ] Redis used as a full cache-first read layer in front of Postgres for redirects (currently config/TTL support only)
- [ ] Background task queue (Celery or arq) for click-event processing, so redirects aren't blocked by analytics writes
- [ ] Horizontal scaling considerations: connection pooling tuning, read replicas
- [ ] Structured logging and request tracing
- [ ] Prometheus metrics + Grafana dashboard for API health
- [ ] Dockerfile + Docker Compose for one-command local/prod-like spin-up
- [ ] CI pipeline (lint, type-check, tests, migration check) on every PR

### 🎨 Frontend / UX
- [ ] Web dashboard (React/Next.js) consuming this API: login, link creation, analytics views
- [ ] Public-facing landing/redirect page with branding
- [ ] Browser extension for one-click shortening

### 🧪 Quality
- [ ] Automated test suite (unit + integration) covering services and repositories
- [ ] Load testing for the redirect path specifically (it's the hottest endpoint)
- [ ] API contract tests against the OpenAPI schema

## License

Add your preferred license (e.g. MIT) and a `LICENSE` file.