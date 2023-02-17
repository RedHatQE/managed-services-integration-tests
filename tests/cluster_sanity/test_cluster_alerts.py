import pytest
import logging
from tests.cluster_sanity.utils import verify_no_listed_alerts_on_cluster, verify_prometheus_connection

TIMEOUT_3MIN = 3*60
Alert_LIST=[
    "KubePodNotReady",
    "KubeNodeUnreachable",
    "ClusterOperatorDown",
]
sample_query = 'sort_desc(sum(sum_over_time(ALERTS{alertstate="firing"}[24h])) by (alertname))'

LOGGER = logging.getLogger(__name__)

class TestClustrAlerts:
    @pytest.mark.smoke
    def test_no_alerts_firing_on_healthy_cluster(
        self,prometheus,
    ):
      cluster_alerts_list = Alert_LIST.copy()
      verify_no_listed_alerts_on_cluster(
        prometheus=prometheus, alerts_list=cluster_alerts_list

      )
    @pytest.mark.smoke
    def test_prometheus_query_response(self,prometheus):
       verify_prometheus_connection(prometheus=prometheus,query=sample_query)