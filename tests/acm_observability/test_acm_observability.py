import pytest
from const import HUB_CLUSTER
from simple_logger.logger import get_logger


LOGGER = get_logger(name=__name__)

pytestmark = pytest.mark.acm_observability


class TestACMObservability:
    def test_hub_etcd_metrics_exists(
        self,
        admin_client_scope_session,
        clusters_etcd_metrics,
    ):
        assert isinstance(
            clusters_etcd_metrics[HUB_CLUSTER][-1], float
        ), "Hub cluster etcd db size metric value is invalid"

    def test_managed_etcd_metrics_exists(
        self, admin_client_scope_session, clusters_etcd_metrics, managed_clusters
    ):
        assert managed_clusters, "No managed clusters metrics found"
        LOGGER.info(f"ACM managed clusters: {managed_clusters}")

        for managed_cluster in managed_clusters:
            assert isinstance(
                clusters_etcd_metrics[managed_cluster][-1], float
            ), f"{managed_cluster} cluster etcd db size metric value is invalid"
