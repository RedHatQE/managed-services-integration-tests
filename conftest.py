import logging
import os
import shutil

import pytest
from ocp_resources.node import Node
from ocp_resources.pod import Pod
from ocp_utilities.infra import get_client
from ocp_wrapper_data_collector.data_collector import (
    collect_pods_data,
    collect_resources_yaml_instance,
    prepare_pytest_item_data_dir,
)
from pyaml_env import parse_config
from pytest_testconfig import config as py_config

from utilities.logger import setup_logging

LOGGER = logging.getLogger(__name__)
BASIC_LOGGER = logging.getLogger("basic")


def separator(symbol_, val=None):
    terminal_width = shutil.get_terminal_size(fallback=(120, 40))[0]
    if not val:
        return f"{symbol_ * terminal_width}"

    sepa = int((terminal_width - len(val) - 2) // 2)
    return f"\n{symbol_ * sepa} {val} {symbol_ * sepa}"


# pytest fixtures
def pytest_addoption(parser):
    data_collector_group = parser.getgroup(name="DataCollector")
    ocm_group = parser.getgroup(name="OCM")
    upgrade_group = parser.getgroup(name="Upgrade")
    cluster_group = parser.getgroup(name="Cluster")

    # Data collector group
    data_collector_group.addoption(
        "--data-collector",
        help=("pass YAML file path to enable data collector to capture additional logs" " and resources"),
    )
    data_collector_group.addoption(
        "--pytest-log-file",
        help="Path to pytest log file",
        default="pytest-tests.log",
    )

    # OCM group
    ocm_group.addoption("--cluster-name", help="Cluster name")

    # Upgrade group
    upgrade_group.addoption("--ocp-target-version", help="cluster OCP target version")

    # Cluster group
    cluster_group.addoption(
        "--kubeconfig-file-paths",
        default="",
        help="""
        str of comma-separated kubeconfig file paths, pass '--kubeconfig-file-path=<path to file>,<path to file>'
        """,
    )


def pytest_generate_tests(metafunc):
    if "kubeconfig_file_paths" in metafunc.fixturenames:
        metafunc.parametrize(
            "kubeconfig_file_paths",
            metafunc.config.getoption("--kubeconfig-file-paths").split(","),
        )


def pytest_sessionstart(session):
    data_collector = session.config.getoption("--data-collector")
    if data_collector:
        py_config["data_collector"] = parse_config(path=data_collector)
        shutil.rmtree(
            py_config["data_collector"]["data_collector_base_directory"],
            ignore_errors=True,
        )

    tests_log_file = session.config.getoption("pytest_log_file")
    if os.path.exists(tests_log_file):
        shutil.rmtree(tests_log_file, ignore_errors=True)

    setup_logging(
        log_file=tests_log_file,
        log_level=session.config.getoption("log_cli_level") or logging.INFO,
    )


def pytest_report_teststatus(report, config):
    test_name = report.head_line
    when = report.when
    call_str = "call"
    if report.passed:
        if when == call_str:
            BASIC_LOGGER.info(f"\nTEST: {test_name} STATUS: \033[0;32mPASSED\033[0m")

    elif report.skipped:
        BASIC_LOGGER.info(f"\nTEST: {test_name} STATUS: \033[1;33mSKIPPED\033[0m")

    elif report.failed:
        if when != call_str:
            BASIC_LOGGER.info(
                f"\nTEST: {test_name} STATUS: [{when}] \033[0;31mERROR\033[0m",
            )
        else:
            BASIC_LOGGER.info(f"\nTEST: {test_name} STATUS: \033[0;31mFAILED\033[0m")


def pytest_runtest_setup(item):
    """
    Use incremental
    """
    BASIC_LOGGER.info(f"\n{separator(symbol_='-', val=item.name)}")
    set_up_pytest_runtest_phase(item=item, phase="SETUP")


def pytest_sessionfinish(session, exitstatus):
    reporter = session.config.pluginmanager.get_plugin("terminalreporter")
    reporter.summary_stats()

    # Remove empty directories from data collector directory
    if session.config.getoption("--data-collector"):
        collector_directory = py_config["data_collector"]["data_collector_base_directory"]
        for root, dirs, files in os.walk(collector_directory, topdown=False):
            for _dir in dirs:
                dir_path = os.path.join(root, _dir)
                if not os.listdir(dir_path):
                    shutil.rmtree(dir_path, ignore_errors=True)


def pytest_runtest_call(item):
    set_up_pytest_runtest_phase(item=item, phase="CALL")


def pytest_runtest_teardown(item):
    set_up_pytest_runtest_phase(item=item, phase="TEARDOWN")


@pytest.fixture(scope="session")
def junitxml_plugin(request, record_testsuite_property):
    return record_testsuite_property if request.config.pluginmanager.has_plugin("junitxml") else None


def pytest_exception_interact(node, call, report):
    BASIC_LOGGER.error(report.longreprtext)
    if node.session.config.getoption("--data-collector") and not node.get_closest_marker(name="skip_data_collector"):
        resources_to_collect = [Node]
        base_directory = py_config["data_collector"]["data_collector_base_directory"]
        try:
            collect_resources_yaml_instance(resources_to_collect=resources_to_collect, base_directory=base_directory)
            pods = list(Pod.get(dyn_client=get_client()))
            collect_pods_data(pods_list=pods, base_directory=base_directory)

        except Exception as exp:
            LOGGER.warning(f"Failed to collect resources: {exp}")
            return


def set_up_pytest_runtest_phase(item, phase):
    BASIC_LOGGER.info(f"{separator(symbol_='-', val=phase)}")
    if item.session.config.getoption("--data-collector") and not item.get_closest_marker(name="skip_data_collector"):
        py_config["data_collector"]["collector_directory"] = prepare_pytest_item_data_dir(
            item=item,
            base_directory=py_config["data_collector"]["data_collector_base_directory"],
            subdirectory_name=phase.lower(),
        )
