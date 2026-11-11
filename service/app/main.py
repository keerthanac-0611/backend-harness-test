from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth_router, customer_router
from app.core.config import Settings, load_settings
from app.db.repository import CustomerRepository
from app.services.customer_service import CustomerService


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or load_settings()
    app = FastAPI(title="Customer Service API", version="1.0.0")
    app.state.settings = settings
    app.state.customer_service = CustomerService(CustomerRepository(settings.db_path), settings)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.include_router(customer_router)
    app.include_router(auth_router)

    @app.get("/health", tags=["ops"])
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
