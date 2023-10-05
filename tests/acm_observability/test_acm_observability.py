import json

import pytest
import requests
from ocp_resources.multi_cluster_observability import MultiClusterObservability
from ocp_resources.route import Route
from simple_logger.logger import get_logger


LOGGER = get_logger(name=__name__)

pytestmark = pytest.mark.acm_observability
etcd_query_expression = "etcd_debugging_mvcc_db_total_size_in_bytes"
observability_ns = "open-cluster-management-observability"


class TestAcmObservability:
    def test_observability_is_ready(self, admin_client_scope_session):
        observability = MultiClusterObservability(
            client=admin_client_scope_session, name="observability"
        )
        assert observability.exists
        assert (
            observability.instance.status.conditions[-1].type
            == observability.Status.READY
        )

    def test_hub_etcd_metrics_exists(self, admin_client_scope_session, kubeadmin_token):
        rbac_proxy_route_url = Route(
            client=admin_client_scope_session,
            name="rbac-query-proxy",
            namespace=observability_ns,
        ).instance.spec.host
        query_headers = {
            "Authorization": f"Bearer {kubeadmin_token}",
        }
        query_res = requests.get(
            url=f"https://{rbac_proxy_route_url}/api/v1/query?query={etcd_query_expression}",
            headers=query_headers,
            verify=False,
        )
        query_data = json.loads(query_res.content.decode())
        latest_etcd_db_size = query_data["data"]["result"][-1]["value"][0]

        float(latest_etcd_db_size)

    def test_managed_etcd_metrics_exists(
        self, admin_client_scope_session, kubeadmin_token
    ):
        # TODO: get managed clusters names
        pass
