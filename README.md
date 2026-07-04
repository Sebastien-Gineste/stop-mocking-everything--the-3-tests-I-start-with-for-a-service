# The Only 3 Tests You Need — Python Example

A small FastAPI service (users + payments) that demonstrates a testing strategy with **unit**, **contract**, and **E2E** tests — plus a mock-heavy anti-pattern for contrast.

## Quick start

```bash
uv sync --extra dev
uv run pytest
uv run uvicorn app.main:app --reload
```

Contract and E2E tests start a **Docker** payment provider (`payment_provider/`) and wire the app via `HttpPaymentGateway`. Docker must be running locally (GitHub Actions includes it).

Run tests by layer:

```bash
uv run pytest -m unit
uv run pytest -m contract
uv run pytest -m e2e
uv run pytest -m antipattern
```

CI runs all tests on push/PR via GitHub Actions (`.github/workflows/ci.yml`).

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/users` | Register a user |
| GET | `/users/{email}` | Get user by email |
| POST | `/payments` | Charge a payment |
| GET | `/payments/{email}` | List payments for a user |

Example:

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"secure-password"}'

curl -X POST http://127.0.0.1:8000/payments \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","amount":25.0,"currency":"EUR"}'
```

## Architecture

```
app/
  domain/          # models + pure validation (no I/O)
  ports/           # ABCs: UserRepository, PaymentRepository, PaymentGateway
  adapters/
    fakes/               # fake repos + fake payment gateway
    real_implementation/ # SQLite repos + HTTP payment gateway
  services/        # orchestration (UserService, PaymentService)
  main.py          # FastAPI routes + DI
payment_provider/  # Docker HTTP external payment service (contract + E2E)
tests/
  conftest.py      # shared Docker payment_provider fixture
  unit/            # validation rules + service orchestration with fakes
  contract/        # same contract against fake AND real adapters
  e2e/             # real wiring (HTTP + SQLite + DI + Docker payment provider)
  mocks_antipattern/  # the "bad" example
```

## The test layers

Unit tests cover validation rules and service orchestration (with fakes). Contract and E2E layers prove adapter promises and real wiring.

### 1. Unit tests (`tests/unit/`)

Two kinds of unit tests, each with its own SUT (System Under Tests) setup in the test file:

- **Pure logic** — validation rules, no dependencies (`test_validation.py`)
- **Service orchestration** — `UserService` / `PaymentService` wired with contract-tested fakes (`test_user_service.py`, `test_payment_service.py`)

```python
class SUTBuilder:
    def __init__(self) -> None:
        self.repository = FakeUserRepository()
        self.service = UserService(self.repository)

    def with_user(self, email: str, password: str) -> SUTBuilder:
        self.service.register_user(email, password)
        return self

    def build(self) -> SUT:
        return SUT(service=self.service, repository=self.repository)

def sut_builder() -> SUTBuilder:
    return SUTBuilder()

def test_register_user_persists_in_fake_repository():
    sut = sut_builder().build()
    result = sut.service.register_user("john@example.com", "secure-password")
    assert sut.repository.find_by_email("john@example.com") is not None
```

### 2. Contract tests (`tests/contract/`)

Test the **promise of each boundary**. The same contract runs against fake and real implementations:

- `FakeUserRepository` vs `SqliteUserRepository`
- `FakePaymentRepository` vs `SqlitePaymentRepository`
- `FakePaymentGateway` vs `HttpPaymentGateway` (real HTTP to a Docker payment provider)

```python
def user_repository_contract(repository):
    user = User(email="john@example.com", password_hash="hashed")
    repository.save(user)
    saved = repository.find_by_email("john@example.com")
    assert saved.email == "john@example.com"
```

### 3. E2E tests (`tests/e2e/`)

Test **real wiring**: FastAPI TestClient, real SQLite, real DI, and `HttpPaymentGateway` calling the Docker payment provider.

```python
def test_user_can_register_and_be_retrieved(client):
    response = client.post("/users", json={...})
    assert response.status_code == 201
```

### Anti-pattern (`tests/mocks_antipattern/`)

Mock-heavy tests that assert method calls instead of behavior. Kept green for educational comparison.

## Prompt for AI-generated tests

Instead of "Generate tests for this service", use:

```text
Generate tests for this service using the following strategy:

1. Write unit tests only for pure business logic.
2. Do not mock repositories, gateways, or external service interfaces by default.
3. Use fake implementations when testing service behavior.
4. For each fake implementation, add contract tests that also run against the real implementation.
5. Add only a small number of end-to-end tests to verify that the real application is correctly wired.
6. Avoid testing implementation details such as internal method calls unless there is a strong reason.
```

## License

This project is licensed under the MIT License.