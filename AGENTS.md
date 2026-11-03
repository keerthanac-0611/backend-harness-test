# Backend repository – agent instructions

You are the **backend repository agent**. This repo owns all **business logic**, persistence and the REST API
for customers. It is the **provider** of the `customer-api` contract (`../../contracts/customer-api.contract.json`).

## Stack
- Python 3.9+, FastAPI, Pydantic v2, SQLite (stdlib `sqlite3`)
- Tests: `pytest` with FastAPI `TestClient`

## Layout (layered – keep dependencies pointing inwards)
| Layer | Path | Responsibility |
|-------|------|----------------|
| API | `app/api/` | Routing, request/response schemas, HTTP error mapping, auth dependency |
| Service | `app/services/` | Business workflows (register, login, view details) |
| Domain | `app/domain/` | Entities, business rules (password policy, normalization), domain errors |
| Persistence | `app/db/` | SQLite repository |
| Core | `app/core/` | Settings, password hashing, JWT tokens |

## Rules
1. Never return `password` / `password_hash` in any response.
2. Any change to a route, status code or response field **must** be reflected in the shared contract and
   called out in your task summary so the integration reviewer can notify consumers.
3. Business rules live in `app/domain` / `app/services`, never in routers.
4. Every behaviour change needs a test in `tests/`.
5. Use Python 3.9 compatible typing (`Optional[...]`, not `X | None`).

## Commands
- Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- Test: `.venv/bin/python -m pytest -q`
- Serve: `.venv/bin/uvicorn app.main:app --port 8000`
