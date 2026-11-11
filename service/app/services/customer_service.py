from typing import Optional, Tuple

from app.core import security
from app.core.config import Settings
from app.db.repository import CustomerRepository
from app.domain.errors import (
    CustomerNotFoundError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)
from app.domain.models import Customer
from app.domain.rules import normalize_email, normalize_name, validate_password_strength


class CustomerService:
    """Business logic for customer registration, authentication and profile lookup."""

    def __init__(self, repository: CustomerRepository, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings

    def register(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Customer:
        email = normalize_email(email)
        validate_password_strength(password)
        if self._repository.get_by_email(email):
            raise EmailAlreadyRegisteredError(email)
        return self._repository.create(
            email=email,
            password_hash=security.hash_password(password),
            first_name=normalize_name(first_name),
            last_name=normalize_name(last_name),
            phone=phone.strip() if phone else None,
            address=address.strip() if address else None,
        )

    def authenticate(self, email: str, password: str) -> Customer:
        customer = self._repository.get_by_email(normalize_email(email))
        # Always run a hash comparison to keep timing similar for unknown emails.
        stored_hash = customer.password_hash if customer else security.hash_password("timing-guard")
        if not security.verify_password(password, stored_hash) or customer is None:
            raise InvalidCredentialsError()
        return customer

    def issue_token(self, customer: Customer) -> Tuple[str, int]:
        ttl = self._settings.token_ttl_minutes * 60
        token = security.create_access_token(str(customer.id), self._settings.secret_key, ttl)
        return token, ttl

    def login(self, email: str, password: str) -> Tuple[Customer, str, int]:
        customer = self.authenticate(email, password)
        token, ttl = self.issue_token(customer)
        return customer, token, ttl

    def resolve_token(self, token: str) -> Customer:
        payload = security.decode_access_token(token, self._settings.secret_key)
        return self.get_customer(int(payload["sub"]))

    def get_customer(self, customer_id: int) -> Customer:
        customer = self._repository.get_by_id(customer_id)
        if customer is None:
            raise CustomerNotFoundError(customer_id)
        return customer
