import pytest
from simple_logger.logger import get_logger


LOGGER = get_logger(name=__name__)

pytestmark = pytest.mark.acm_observability


class TestACMObservability:
    def test_hub_etcd_metrics_exists(
        self,
        admin_client_scope_session,
        multi_cluster_observability,
        etcd_metrics_query,
    ):
        latest_etcd_db_size = etcd_metrics_query["data"]["result"][-1]["value"][0]
        LOGGER.info(
            "Metrics retrieved on hub cluster etcd db size from ACM"
            f" observability:\n{etcd_metrics_query}"
        )

        assert type(latest_etcd_db_size) is float

    def test_managed_etcd_metrics_exists(
        self,
        admin_client_scope_session,
        multi_cluster_observability,
        etcd_metrics_query,
    ):
        # TODO: get managed clusters names
        pass
