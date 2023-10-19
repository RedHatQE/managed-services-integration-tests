import pytest
from const import HUB_CLUSTER


pytestmark = pytest.mark.acm_observability


def cluster_etcd_metrics_value_is_valid(clusters_etcd, cluster_name):
    # Checking the last etcd db size metric updated via observability
    latest_etcd_db_size = clusters_etcd[cluster_name][-1]
    return isinstance(latest_etcd_db_size, float) and latest_etcd_db_size > 0


class TestACMObservability:
    def test_hub_etcd_metrics_exist(
        self,
        clusters_etcd_metrics,
    ):
        assert cluster_etcd_metrics_value_is_valid(
            clusters_etcd=clusters_etcd_metrics, cluster_name=HUB_CLUSTER
        ), (
            "Hub cluster etcd db size metric value is invalid:"
            f" {clusters_etcd_metrics[HUB_CLUSTER][-1]}"
        )

    def test_managed_etcd_metrics_exist(
        self, clusters_etcd_metrics, observability_managed_clusters
    ):
        for managed_cluster in observability_managed_clusters:
            assert cluster_etcd_metrics_value_is_valid(
                clusters_etcd=clusters_etcd_metrics, cluster_name=managed_cluster
            ), (
                f"{managed_cluster} cluster etcd db size metric value is invalid:"
                f" {clusters_etcd_metrics[managed_cluster][-1]}"
            )
