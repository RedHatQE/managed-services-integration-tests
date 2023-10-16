import os

import pytest
import requests
from const import HUB_CLUSTER
from ocp_resources.multi_cluster_observability import MultiClusterObservability
from ocp_resources.route import Route
from pytest_testconfig import config as py_config


@pytest.fixture(scope="session")
def multi_cluster_observability(admin_client_scope_session):
    observability_name = "observability"
    observability = MultiClusterObservability(
        client=admin_client_scope_session,
        name=observability_name,
    )
    assert (
        observability.exists
    ), f"{observability_name} MultiClusterObservability does not exist"
    assert (
        observability.instance.status.conditions[-1].type == observability.Status.READY
    )

    return observability


@pytest.fixture(scope="session")
def rbac_proxy_route_url(admin_client_scope_session, multi_cluster_observability):
    rbac_proxy_route_name = "rbac-query-proxy"
    rbac_proxy_route_url = Route(
        client=admin_client_scope_session,
        name=rbac_proxy_route_name,
        namespace="open-cluster-management-observability",
    )
    assert rbac_proxy_route_url.exists, f"{rbac_proxy_route_name} Route does not exist"

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
    assert query_result.ok, (
        f"Query request failed with status {query_result.status_code}:"
        f" {query_result.reason}"
    )

    return query_result.json()["data"]["result"]


@pytest.fixture(scope="session")
def clusters_etcd_metrics(etcd_metrics_query):
    clusters_etcd_metrics = {}

    for metric_result in etcd_metrics_query:
        metric_cluster = metric_result["metric"]["cluster"]
        cluster_etcd_db_size = metric_result["value"][0]
        if metric_cluster in clusters_etcd_metrics.keys():
            clusters_etcd_metrics[metric_cluster].append(cluster_etcd_db_size)
        else:
            clusters_etcd_metrics[metric_cluster] = [cluster_etcd_db_size]

    return clusters_etcd_metrics


@pytest.fixture(scope="session")
def kubeadmin_token():
    kubeadmin_token_env_var_name = "KUBEADMIN_TOKEN"
    token = os.getenv(kubeadmin_token_env_var_name, py_config["kubeadmin_token"])

    assert token, (
        f"{kubeadmin_token_env_var_name} is not set neither as an environment variable"
        " or an argument."
    )
    return token


@pytest.fixture(scope="session")
def managed_clusters(clusters_etcd_metrics):
    managed_clusters = [
        cluster for cluster in clusters_etcd_metrics.keys() if cluster != HUB_CLUSTER
    ]

    return managed_clusters
