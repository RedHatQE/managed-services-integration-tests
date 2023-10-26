import json
import os
import shlex

import pytest
import requests
from const import HUB_CLUSTER
from ocp_resources.multi_cluster_observability import MultiClusterObservability
from ocp_resources.route import Route
from ocp_utilities.utils import run_command
from pytest_testconfig import config as py_config
from simple_logger.logger import get_logger


LOGGER = get_logger(name=__name__)


@pytest.fixture(scope="session")
def multi_cluster_observability(admin_client_scope_session):
    observability = MultiClusterObservability(
        client=admin_client_scope_session,
        name="observability",
    )
    assert (
        observability.exists
    ), f"{observability.name} MultiClusterObservability does not exist"
    observability.wait_for_condition(
        condition=observability.Condition.READY,
        status=observability.Condition.Status.TRUE,
        timeout=5,
    )

    return observability


@pytest.fixture(scope="session")
def rbac_proxy_route_url(admin_client_scope_session, multi_cluster_observability):
    rbac_proxy_route = Route(
        client=admin_client_scope_session,
        name="rbac-query-proxy",
        namespace="open-cluster-management-observability",
    )
    assert rbac_proxy_route.exists, f"{rbac_proxy_route.name} Route does not exist"

    return rbac_proxy_route.instance.spec.host


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
        clusters_etcd_metrics.setdefault(metric_result["metric"]["cluster"], []).append(
            metric_result["value"][0]
        )

    return clusters_etcd_metrics


@pytest.fixture(scope="session")
def kubeadmin_token():
    kubeadmin_token_env_var_name = "KUBEADMIN_TOKEN"
    token = os.getenv(
        kubeadmin_token_env_var_name, py_config.get("kubeadmin_token", "")
    )

    assert token, (
        f"{kubeadmin_token_env_var_name} is not set neither as an environment variable"
        " or via pytest command line using --tc:kubeadmin_token=<kubeadmin token>"
    )
    return token


@pytest.fixture(scope="session")
def observability_reported_managed_clusters(clusters_etcd_metrics):
    managed_clusters = [
        cluster for cluster in clusters_etcd_metrics if cluster != HUB_CLUSTER
    ]
    assert managed_clusters, "No managed clusters metrics found"
    LOGGER.info(f"Observability reported managed clusters: {managed_clusters}")

    return managed_clusters


@pytest.fixture(scope="session")
def acm_clusters():
    success_res, clusters_res, err_reason = run_command(
        command=shlex.split("cm get clusters -o json"), timeout=15
    )

    # Since cm cli returns acm clusters data even if command fails. see issue below:
    # https://github.com/stolostron/cm-cli/issues/256
    assert (
        success_res or clusters_res
    ), f"Failed to get ACM clusters via cm cli: {err_reason}"

    return json.loads(clusters_res)["items"]


@pytest.fixture(scope="session")
def acm_managed_clusters(acm_clusters):
    managed_clusters = []

    for i in range(len(acm_clusters)):
        acm_cluster = acm_clusters[i]["metadata"]["labels"]["name"]
        if acm_cluster != HUB_CLUSTER:
            managed_clusters.append(acm_cluster)

    assert managed_clusters, "No ACM managed clusters found"
    LOGGER.info(f"ACM managed clusters: {managed_clusters}")

    return managed_clusters
