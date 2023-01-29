# managed kafka variables
KAFKA_NAME = "ms-kafka"
KAFKA_CLOUD_PROVIDER = "aws"
KAFKA_REGION = "us-east-1"
KAFKA_PLAN = "developer.x1"
KAFKA_TIMEOUT = 360
KAFKA_SA_NAME = "ms-kafka-sa"
PARTITION = 0
KAFKA_TOPICS = [
    {
        "name": "debezium_topics",
        "topics": [
            "avro",
            "avro.inventory.addresses",
            "avro.inventory.customers",
            "avro.inventory.geom",
            "avro.inventory.orders",
            "avro.inventory.products",
            "avro.inventory.products_on_hand",
            "schema-changes.inventory",
        ],
        "cleanup_policy": "delete",
        "num_partitions": 1,
    },
    {
        "name": "mysql_topics",
        "topics": [
            "debezium-cluster-configs",
            "debezium-cluster-offsets",
            "debezium-cluster-status",
        ],
        "cleanup_policy": "compact",
        "num_partitions": 1,
    },
]

# debezium variables
DEBEZIUM_NS = "mas-debezium"
CONSUMER_POD = "kafka-consumer-pod"
