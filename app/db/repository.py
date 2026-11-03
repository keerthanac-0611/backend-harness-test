import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator, Optional

from app.domain.errors import EmailAlreadyRegisteredError
from app.domain.models import Customer

SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    created_at TEXT NOT NULL
)
"""


class CustomerRepository:
    """SQLite-backed persistence for customers."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        directory = os.path.dirname(db_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with self._connect() as conn:
            conn.execute(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _to_customer(row: Optional[sqlite3.Row]) -> Optional[Customer]:
        return Customer(**dict(row)) if row else None

    def get_by_email(self, email: str) -> Optional[Customer]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM customers WHERE email = ?", (email,)).fetchone()
        return self._to_customer(row)

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
        return self._to_customer(row)

    def create(
        self,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        phone: Optional[str],
        address: Optional[str],
    ) -> Customer:
        created_at = datetime.now(timezone.utc).isoformat()
        try:
            with self._connect() as conn:
                cursor = conn.execute(
                    "INSERT INTO customers (email, password_hash, first_name, last_name, phone, address, created_at)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (email, password_hash, first_name, last_name, phone, address, created_at),
                )
                customer_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            raise EmailAlreadyRegisteredError(email)
        return Customer(customer_id, email, password_hash, first_name, last_name, phone, address, created_at)
