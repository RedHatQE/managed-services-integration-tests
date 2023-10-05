import json

import pytest
import requests
from ocp_resources.multi_cluster_observability import MultiClusterObservability
from ocp_resources.route import Route


@pytest.fixture(scope="session")
def rbac_proxy_route_url(admin_client_scope_session):
    rbac_proxy_route_url = Route(
        client=admin_client_scope_session,
        name="rbac-query-proxy",
        namespace="open-cluster-management-observability",
    )
    assert rbac_proxy_route_url.exists

    return rbac_proxy_route_url.instance.spec.host


@pytest.fixture(scope="session")
def etcd_metrics_query(rbac_proxy_route_url, kubeadmin_token):
    query_headers = {
        "Authorization": f"Bearer {kubeadmin_token}",
    }
    query_result = requests.get(
        url=f"https://{rbac_proxy_route_url}/api/v1/query?query=etcd_debugging_mvcc_db_total_size_in_bytes",
        headers=query_headers,
        verify=False,
    )
    assert query_result.ok

    query_data = json.loads(query_result.content.decode())
    return query_data


@pytest.fixture(scope="session")
def multi_cluster_observability(admin_client_scope_session):
    observability = MultiClusterObservability(
        client=admin_client_scope_session, name="observability"
    )
    assert observability.exists
    assert (
        observability.instance.status.conditions[-1].type == observability.Status.READY
    )

    return observability
