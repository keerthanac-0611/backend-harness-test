from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_current_customer, get_customer_service
from app.api.schemas import (
    CustomerResponse,
    CustomerSummaryResponse,
    ErrorResponse,
    LoginRequest,
    RegistrationRequest,
    TokenResponse,
)
from app.domain.errors import (
    CustomerNotFoundError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    WeakPasswordError,
)
from app.domain.models import Customer
from app.services.customer_service import CustomerService

customer_router = APIRouter(prefix="/api/customers", tags=["customers"])
auth_router = APIRouter(prefix="/api/auth", tags=["auth"])


def to_response(customer: Customer) -> CustomerResponse:
    return CustomerResponse(
        id=customer.id,
        email=customer.email,
        first_name=customer.first_name,
        last_name=customer.last_name,
        phone=customer.phone,
        address=customer.address,
        created_at=customer.created_at,
    )


def to_summary(customer: Customer) -> CustomerSummaryResponse:
    return CustomerSummaryResponse(
        id=customer.id, first_name=customer.first_name, last_name=customer.last_name
    )


@customer_router.post(
    "/register",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse}},
)
def register_customer(
    payload: RegistrationRequest, service: CustomerService = Depends(get_customer_service)
) -> CustomerResponse:
    try:
        customer = service.register(**payload.model_dump())
    except EmailAlreadyRegisteredError:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email is already registered")
    except WeakPasswordError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    return to_response(customer)


@auth_router.post("/login", response_model=TokenResponse, responses={401: {"model": ErrorResponse}})
def login(payload: LoginRequest, service: CustomerService = Depends(get_customer_service)) -> TokenResponse:
    try:
        customer, token, ttl = service.login(payload.email, payload.password)
    except InvalidCredentialsError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return TokenResponse(access_token=token, expires_in=ttl, customer=to_response(customer))


@customer_router.get("/me", response_model=CustomerResponse, responses={401: {"model": ErrorResponse}})
def get_my_details(current: Customer = Depends(get_current_customer)) -> CustomerResponse:
    return to_response(current)


@customer_router.get("", response_model=List[CustomerSummaryResponse])
def list_customers(service: CustomerService = Depends(get_customer_service)) -> List[CustomerSummaryResponse]:
    return [to_summary(customer) for customer in service.list_customers()]


@customer_router.get("/search", response_model=List[CustomerSummaryResponse])
def search_customers(
    name: str = Query(...), service: CustomerService = Depends(get_customer_service)
) -> List[CustomerSummaryResponse]:
    return [to_summary(customer) for customer in service.search_customers(name)]


@customer_router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def get_customer_details(
    customer_id: int,
    current: Customer = Depends(get_current_customer),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    if customer_id != current.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="You may only view your own details")
    try:
        return to_response(service.get_customer(customer_id))
    except CustomerNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Customer not found")
