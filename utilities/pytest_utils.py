import logging

import pytest as pytest

import ocp_utilities


LOGGER = logging.getLogger(__name__)


# TODO: Remove once added to openshift-python-utilities
def exit_pytest_execution(
    message,
    return_code=99,
    filename=None,
    junitxml_property=None,
):
    """Exit pytest execution

    Exit pytest execution; invokes pytest_sessionfinish.
    Optionally, log an error message to tests-collected-info/utilities/pytest_exit_errors/<filename>

    Args:
        message (str):  Message to display upon exit and to log in errors file
        return_code (int. Default: 99): Exit return code
        filename (str, optional. Default: None): filename where the given message will be saved
        junitxml_property (pytest plugin): record_testsuite_property
    """
    if filename:
        ocp_utilities.data_collector.write_to_file(
            file_name=filename,
            content=message,
            extra_dir_name="pytest_exit_errors",
        )
    if junitxml_property:
        junitxml_property(name="exit_code", value=return_code)
    pytest.exit(msg=message, returncode=return_code)
