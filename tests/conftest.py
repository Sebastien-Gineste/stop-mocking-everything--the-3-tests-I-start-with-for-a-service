from __future__ import annotations

import time
from pathlib import Path

import httpx
import pytest

PAYMENT_PROVIDER_DIR = Path(__file__).resolve().parents[1] / "payment_provider"
PAYMENT_PROVIDER_IMAGE = "only3tests-payment-provider:test"


def wait_for_health(base_url: str, timeout: float = 60) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = httpx.get(f"{base_url}/health", timeout=1)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.5)
    raise RuntimeError("Payment provider did not become healthy in time")


@pytest.fixture(scope="session")
def payment_provider_url() -> str:
    pytest.importorskip("testcontainers")

    try:
        import docker
        from testcontainers.core.container import DockerContainer

        client = docker.from_env()
        client.images.build(
            path=str(PAYMENT_PROVIDER_DIR),
            tag=PAYMENT_PROVIDER_IMAGE,
            rm=True,
        )
    except Exception as exc:
        pytest.skip(f"Docker required for payment provider tests: {exc}")

    container = DockerContainer(PAYMENT_PROVIDER_IMAGE).with_exposed_ports(8080)
    container.start()
    try:
        host = container.get_container_host_ip()
        port = int(container.get_exposed_port(8080))
        base_url = f"http://{host}:{port}"
        wait_for_health(base_url)
        yield base_url
    finally:
        container.stop()
