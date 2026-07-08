# Stop Mocking Everything: The 3 Tests I Start With for a Service — Python Example

Companion code for the article: [Stop Mocking Everything: The 3 Tests I Start With for a Service](https://medium.com/).

This repository demonstrates a test strategy for a service with:
- **unit tests** for pure logic
- **sociable service tests** with real collaborators and verified fakes at ports
- **contract tests** shared by fake and real adapters
- **end-to-end tests** for real wiring
- a **mock-heavy anti-pattern** kept for educational contrast

## Quick start

```bash
uv sync --extra dev
uv run pytest
uv run uvicorn app.main:app --reload
```

Contract and E2E tests start a Docker payment provider from `payment_provider/`.
Docker must be running locally.

Run tests by layer:

```bash
uv run pytest -m unit
uv run pytest -m service
uv run pytest -m contract
uv run pytest -m e2e
uv run pytest -m antipattern
```

## Article section to code map

| Article section | Code in this repo |
|---|---|
| Unit tests for pure logic | `tests/unit/test_validation.py` |
| Sociable service tests | `tests/unit/test_user_service.py`, `tests/unit/test_payment_service.py` |
| Contract tests (verified fakes) | `tests/contract/test_user_repository_contract.py`, `tests/contract/test_payment_repository_contract.py`, `tests/contract/test_payment_gateway_contract.py` |
| E2E tests for wiring | `tests/e2e/test_user_and_payment_flow.py` |
| Mock-everything anti-pattern | `tests/mocks_antipattern/test_user_service_mock_heavy.py`, `tests/mocks_antipattern/test_payment_service_mock_heavy.py` |

Diagram assets used by the article are available in `assets/`:
- `assets/Mocks-tests-Page-1.drawio-b8ce60ca-55e8-4f73-b1ca-704ab856e24a.png`
- `assets/Mocks-tests-Page-4.drawio-0ec4e2ef-9497-499b-82d6-dfd923db0a1d.png`
- `assets/Mocks-tests-Copie_de_Page-1.drawio-9337924a-7305-42ab-b9c0-12ef91d3b378.png`

## Architecture

```text
app/
  domain/          # models + pure validation (no I/O)
  ports/           # ABCs: UserRepository, PaymentRepository, PaymentGateway
  adapters/        # SQLite repos + HTTP payment gateway
  services/        # orchestration + real internal collaborators
  main.py          # FastAPI routes + DI
payment_provider/  # Docker HTTP external payment service (contract + E2E)
tests/
  conftest.py          # shared Docker payment_provider fixture
  doubles/             # shared test doubles (*_fake.py, *_stub.py, *_spy.py)
  unit/                # pure logic + sociable service tests
  contract/            # same contract against fake and real adapters
  e2e/                 # real wiring (HTTP + SQLite + DI + Docker provider)
  mocks_antipattern/   # mock-heavy examples
```

## The test layers

### 1) Unit tests (pure logic)

`tests/unit/test_validation.py` covers deterministic business rules with no dependencies.

### 2) Sociable service tests (real collaborators + verified fakes)

`tests/unit/test_user_service.py` and `tests/unit/test_payment_service.py` run real service logic with real internal collaborators.
At boundaries, they use fakes that are contract-tested against real adapters.

`PaymentService` includes a real internal collaborator (`PaymentEligibilityChecker`) to illustrate the sociable pattern.

### 3) Contract tests (fake vs real)

Each boundary defines a contract function and executes it against both implementations:
- fake adapter (`tests/doubles/`)
- real adapter (`app/adapters/`)

### 4) E2E tests (wiring)

`tests/e2e/test_user_and_payment_flow.py` runs through FastAPI, DI, SQLite, and the real HTTP payment gateway against a Docker provider.

### 5) Anti-pattern suite

`tests/mocks_antipattern/` intentionally shows mock-heavy tests that assert calls and order more than behavior.

## Test doubles in this repo

- **Location**: all reusable test doubles live in `tests/doubles/`
- **Naming**: `*_fake.py`, `*_stub.py`, `*_spy.py`
- **Fake**: `FakeUserRepository`, `FakePaymentRepository`, `FakePaymentGateway`
- **Stub**: `PaymentGatewayDownStub` forces the "gateway down" scenario
- **Spy**: `FakePaymentGateway` records charges in `charges` for post-condition assertions
- **Mock**: `tests/mocks_antipattern/` uses `unittest.mock.Mock` to demonstrate over-mocking

## What contract tests do not guarantee

Contract tests improve trust in fakes for promises that are explicitly tested.
They do not automatically guarantee behaviors that are not in the contract, such as:
- transaction isolation semantics
- concurrency behavior under load
- adapter-specific failure modes you did not encode in the contract

This example uses SQLite for lightweight portability.
If you need to demonstrate production-specific guarantees (for example PostgreSQL locking behavior), add dedicated integration or E2E tests against that real adapter.

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

## CI

CI runs test layers separately on push and pull requests via `.github/workflows/ci.yml`.

## License

This project is licensed under the MIT License.