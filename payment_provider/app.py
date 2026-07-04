from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Payment Provider Stub")
_counter = 0


class ChargeRequest(BaseModel):
    user_email: str
    amount: float = Field(gt=0)
    currency: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/charge")
def charge(payload: ChargeRequest) -> dict[str, str]:
    global _counter
    _counter += 1
    return {
        "transaction_id": f"stub-txn-{_counter}",
        "status": "succeeded",
    }
