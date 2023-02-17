import pytest

from ocp_utilities.monitoring import (
    Prometheus
)

@pytest.fixture(scope="session")
def prometheus():
    return Prometheus()