import pytest
from ocp_resources.node import Node
from ocp_resources.pod import Pod
from ocp_utilities.infra import get_client

from utilities.infra import cluster_sanity


@pytest.fixture()
def admin_client_from_file(kubeconfig_file_path):
    return get_client(config_file=kubeconfig_file_path)


@pytest.fixture(scope="session")
def pods_scope_session(admin_client):
    return list(Pod.get(dyn_client=admin_client))


@pytest.fixture()
def pods_scope_function(admin_client_from_file):
    return list(Pod.get(dyn_client=admin_client_from_file))


@pytest.fixture()
def nodes_scope_function(admin_client_from_file):
    yield list(Node.get(dyn_client=admin_client_from_file))


@pytest.mark.smoke
def test_cluster_sanity(nodes_scope_session, pods_scope_session, junitxml_plugin):
    cluster_sanity(
        nodes=nodes_scope_session,
        pods=pods_scope_session,
        junitxml_property=junitxml_plugin,
    )


@pytest.mark.smoke_multi
def test_multi_clusters_sanity(
    nodes_scope_function, pods_scope_function, junitxml_plugin
):
    cluster_sanity(
        nodes=nodes_scope_function,
        pods=pods_scope_function,
        junitxml_property=junitxml_plugin,
    )
