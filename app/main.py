from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from app.container import Container
from app.domain.models import Payment, User
from app.ports.payment_gateway import PaymentGateway


class UserCreateRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    email: str


class PaymentCreateRequest(BaseModel):
    email: str
    amount: float = Field(gt=0)
    currency: str = "EUR"


class PaymentResponse(BaseModel):
    user_email: str
    amount: float
    currency: str
    transaction_id: str
    status: str


def get_container(request: Request) -> Container:
    return request.app.state.container


def get_user_service(container: Container = Depends(get_container)):
    return container.user_service


def get_payment_service(container: Container = Depends(get_container)):
    return container.payment_service


def create_app(container: Container | None = None) -> FastAPI:
    app_container = container or Container()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.container = app_container
        yield

    app = FastAPI(
        title="Stop Mocking Everything: The 3 Tests I Start With for a Service",
        lifespan=lifespan,
    )
    app.state.container = app_container

    @app.post("/users", status_code=201, response_model=UserResponse)
    def register_user(payload: UserCreateRequest, user_service=Depends(get_user_service)):
        result = user_service.register_user(payload.email, payload.password)
        if result.is_error():
            if result.error == "User already exists":
                raise HTTPException(status_code=409, detail=result.error)
            raise HTTPException(status_code=422, detail=result.error)
        user: User = result.unwrap()
        return UserResponse(email=user.email)

    @app.get("/users/{email}", response_model=UserResponse)
    def get_user(email: str, container: Container = Depends(get_container)):
        user = container.user_repository.find_by_email(email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(email=user.email)

    @app.post("/payments", status_code=201, response_model=PaymentResponse)
    def create_payment(
        payload: PaymentCreateRequest,
        payment_service=Depends(get_payment_service),
    ):
        result = payment_service.charge(payload.email, payload.amount, payload.currency)
        if result.is_error():
            if result.error == "User not found":
                raise HTTPException(status_code=404, detail=result.error)
            raise HTTPException(status_code=422, detail=result.error)
        payment: Payment = result.unwrap()
        return PaymentResponse(
            user_email=payment.user_email,
            amount=payment.amount,
            currency=payment.currency,
            transaction_id=payment.transaction_id,
            status=payment.status,
        )

    @app.get("/payments/{email}", response_model=list[PaymentResponse])
    def list_payments(email: str, container: Container = Depends(get_container)):
        payments = container.payment_repository.find_by_user_email(email)
        return [
            PaymentResponse(
                user_email=payment.user_email,
                amount=payment.amount,
                currency=payment.currency,
                transaction_id=payment.transaction_id,
                status=payment.status,
            )
            for payment in payments
        ]

    return app


app = create_app()