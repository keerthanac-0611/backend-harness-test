import os
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Settings:
    db_path: str = "data/customers.db"
    secret_key: str = "dev-insecure-secret-change-me"
    token_ttl_minutes: int = 60
    cors_origins: List[str] = field(default_factory=lambda: ["http://localhost:5173"])


def load_settings() -> Settings:
    origins = os.getenv("CUSTOMER_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return Settings(
        db_path=os.getenv("CUSTOMER_DB_PATH", "data/customers.db"),
        secret_key=os.getenv("CUSTOMER_SECRET_KEY", "dev-insecure-secret-change-me"),
        token_ttl_minutes=int(os.getenv("CUSTOMER_TOKEN_TTL_MINUTES", "60")),
        cors_origins=[o.strip() for o in origins.split(",") if o.strip()],
    )
