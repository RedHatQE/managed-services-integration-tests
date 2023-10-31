import pytest
from const import HUB_CLUSTER


pytestmark = pytest.mark.acm_observability


def assert_cluster_etcd_metrics_value_is_valid(clusters_etcd, cluster_name):
    # Checking given cluster's last etcd db size metric updated via observability
    latest_etcd_db_size = clusters_etcd[cluster_name][-1]
    assert isinstance(latest_etcd_db_size, float) and latest_etcd_db_size > 0, (
        f"{cluster_name} cluster etcd db size metric value is invalid:"
        f" {latest_etcd_db_size}"
    )


class TestACMObservability:
    def test_all_clusters_metrics_reported(
        self, observability_reported_managed_clusters, acm_managed_clusters
    ):
        observability_not_reported_clusters = [
            cluster
            for cluster in acm_managed_clusters
            if cluster not in observability_reported_managed_clusters
        ]
        assert not observability_not_reported_clusters, (
            "Not all ACM clusters "
            f"are reported via observability: {observability_not_reported_clusters}, "
            f"clusters expected: {acm_managed_clusters}"
        )

    def test_hub_etcd_metrics_exist_and_valid(
        self,
        clusters_etcd_metrics,
    ):
        assert_cluster_etcd_metrics_value_is_valid(
            clusters_etcd=clusters_etcd_metrics, cluster_name=HUB_CLUSTER
        )

    def test_managed_etcd_metrics_exist_and_valid(
        self, clusters_etcd_metrics, observability_reported_managed_clusters
    ):
        for managed_cluster in observability_reported_managed_clusters:
            assert_cluster_etcd_metrics_value_is_valid(
                clusters_etcd=clusters_etcd_metrics, cluster_name=managed_cluster
            )
