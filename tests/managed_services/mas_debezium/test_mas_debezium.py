import pytest
from constants import PARTITION
from rhoas_kafka_instance_sdk.api import records_api
from rhoas_kafka_instance_sdk.model.record import Record


pytestmark = pytest.mark.mas_debezium


def test_kafka_topics(
    kafka_instance_client,
    kafka_topics,
    # kafka_instance_sa,
    # consumer_pod
):
    """
    Test for managed kafka resources setup,
    usage and teardown via rhoas sdk
    """
    # Produce to avro.inventory.customers topic
    records_api_client = records_api.RecordsApi(api_client=kafka_instance_client)
    topic_name = "avro.inventory.customers"
    record_msg = "This is a topic test record"
    record = Record(value=record_msg, partition=PARTITION)
    records_api_client.produce_record(topic_name=topic_name, record=record)

    # Consume from avro.inventory.customers topic
    # TODO: raises ApiValueError (known bug) work with Dimitri to resolve this
    consume_topic_res = records_api_client.consume_records(
        topic_name=topic_name, partition=PARTITION
    )
    assert consume_topic_res[0].value == record_msg
