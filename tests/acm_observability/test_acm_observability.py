import pytest
from const import HUB_CLUSTER


pytestmark = pytest.mark.acm_observability


class TestACMObservability:
    def test_hub_etcd_metrics_exist(
        self,
        clusters_etcd_metrics,
    ):
        latest_hub_etcd_db_size = clusters_etcd_metrics[HUB_CLUSTER][-1]
        assert (
            isinstance(latest_hub_etcd_db_size, float)
            and latest_hub_etcd_db_size >= 0.0
        ), (
            "Hub cluster etcd db size metric value is invalid:"
            f" {latest_hub_etcd_db_size}"
        )

    def test_managed_etcd_metrics_exist(self, clusters_etcd_metrics, managed_clusters):
        for managed_cluster in managed_clusters:
            latest_managed_etcd_db_size = clusters_etcd_metrics[managed_cluster][-1]
            assert (
                isinstance(latest_managed_etcd_db_size, float)
                and latest_managed_etcd_db_size >= 0.0
            ), (
                f"{managed_cluster} cluster etcd db size metric value is invalid:"
                f" {latest_managed_etcd_db_size}"
            )
