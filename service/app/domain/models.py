from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Customer:
    id: int
    email: str
    password_hash: str
    first_name: str
    last_name: str
    phone: Optional[str]
    address: Optional[str]
    created_at: str
