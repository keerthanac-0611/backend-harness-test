from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import InvalidTokenError
from app.domain.errors import CustomerNotFoundError
from app.domain.models import Customer
from app.services.customer_service import CustomerService

_bearer = HTTPBearer(auto_error=False)


def get_customer_service(request: Request) -> CustomerService:
    return request.app.state.customer_service


def get_current_customer(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    service: CustomerService = Depends(get_customer_service),
) -> Customer:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized
    try:
        return service.resolve_token(credentials.credentials)
    except (InvalidTokenError, CustomerNotFoundError, KeyError, ValueError):
        raise unauthorized
