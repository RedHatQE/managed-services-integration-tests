import shlex

import pytest
from constants import TEST_RECORD


pytestmark = pytest.mark.mas_debezium


class TestDebezium:
    def test_kafka_topics(self, kafka_record, kafka_sa_acl, consumer_pod):
        """
        Test for managed kafka resources setup,
        usage and teardown via rhoas sdk
        """
        # Get consumed record from test topic via kcat pod
        consumed_event = consumer_pod.execute(
            container=consumer_pod.name,
            command=shlex.split(
                s=f"kcat -b {consumer_pod.kafka_bootstrap_url} "
                "-X sasl.mechanisms=PLAIN "
                "-X security.protocol=SASL_SSL "
                f"-X sasl.username={consumer_pod.kafka_sa_client_id} "
                f"-X sasl.password={consumer_pod.kafka_sa_client_secret} "
                f"-t {consumer_pod.kafka_test_topic} -C -e"
            ),
        )
        assert (
            consumed_event.strip("\n") == TEST_RECORD
        ), f"Failed to consume the correct record. Existing Kafka event:\n{consumed_event}"
