import pytest
from simple_logger.logger import get_logger


LOGGER = get_logger(name=__name__)

pytestmark = pytest.mark.acm_observability
HUB_CLUSTER = "local-cluster"


class TestACMObservability:
    def test_hub_etcd_metrics_exists(
        self,
        admin_client_scope_session,
        clusters_etcd_metrics,
    ):
        latest_hub_etcd_metric = clusters_etcd_metrics[HUB_CLUSTER][-1]
        assert (
            type(latest_hub_etcd_metric) is float
        ), "etcd db size metric value is invalid"

    def test_managed_etcd_metrics_exists(
        self,
        admin_client_scope_session,
        clusters_etcd_metrics,
    ):
        managed_clusters = [
            cluster
            for cluster in clusters_etcd_metrics.keys()
            if cluster != HUB_CLUSTER
        ]
        assert managed_clusters, "No managed clusters metrics found"
        LOGGER.info(f"ACM managed clusters: {managed_clusters}")

        for managed_cluster in managed_clusters:
            latest_managed_etcd_metric = clusters_etcd_metrics[managed_cluster][-1]
            assert type(latest_managed_etcd_metric) is float
