# Development Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Docker & Docker Compose (recommended)

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd idol-platform

# Copy environment config
cp .env.example .env
# Edit .env — at minimum set:
#   HQ_BOT_TOKEN
#   FOUNDER_TELEGRAM_ID
#   DATABASE_URL

# Start PostgreSQL
make up

# Install Python dependencies
make install

# Run migrations
make migrate

# Start the bot
make run
```

## Common Commands

```bash
make test          # Run tests
make test-cov      # Tests with coverage
make lint          # Run ruff linter
make format        # Auto-format code
make typecheck     # Run mypy
make migration msg="add X table"  # Create new migration
make db-shell      # Open psql
make logs          # Docker logs
make shell         # Python REPL with config loaded
```

## Development Phases

1. ✅ Phase 1 — Repository structure + config + Docker
2. ⬜ Phase 2 — Database (engine, tables, Alembic, seed)
3. ⬜ Phase 3 — Identity (user repo, identity service, founder bootstrap)
4. ⬜ Phase 4 — Roles + Permissions (RBAC, auth service, auth middleware)
5. ⬜ Phase 5 — HQ Bot foundation (/start, keyboards, callbacks)
6. ⬜ Phase 6 — IDOL TEAM integration (notifications, topic routing)
7. ⬜ Phase 7 — Audit + logging
8. ⬜ Phase 8 — Testing (full test suite)

## Code Style

- Follow ruff rules (configured in pyproject.toml)
- Type hints everywhere
- Async by default
- No business logic in handlers
- No os.getenv() outside config.py
