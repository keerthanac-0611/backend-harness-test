# Customer Service – Backend (FastAPI)

Business logic for **Customer Registration**, **Login** and **View Customer Details**.

## Run
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000   # docs at http://127.0.0.1:8000/docs
.venv/bin/python -m pytest -q
```

## API
| Method | Path | Auth | Success | Errors |
|--------|------|------|---------|--------|
| POST | `/api/customers/register` | – | 201 Customer | 409 duplicate email, 422 validation |
| POST | `/api/auth/login` | – | 200 Token (+customer) | 401 invalid credentials, 422 |
| GET | `/api/customers/me` | Bearer | 200 Customer | 401 |
| GET | `/api/customers/{customer_id}` | Bearer | 200 Customer | 401, 403 (not own record), 404 |
| GET | `/health` | – | 200 | – |

Password policy: 8–128 chars, at least one uppercase, one lowercase and one digit.

## Configuration (env vars)
| Variable | Default |
|----------|---------|
| `CUSTOMER_DB_PATH` | `service` |
| `CUSTOMER_SECRET_KEY` | `dev-insecure-secret-change-me` (**override in production**) |
| `CUSTOMER_TOKEN_TTL_MINUTES` | `60` |
| `CUSTOMER_CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` |
