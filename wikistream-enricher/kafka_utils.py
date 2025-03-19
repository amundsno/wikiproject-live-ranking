import time
import json
import logging

from kafka.errors import NoBrokersAvailable
from kafka import KafkaProducer, KafkaConsumer


def init_kafka_consumer(bootstrap_server: str, topic: str, group_id: str, retries: int = 5, delay: int = 5) -> KafkaConsumer:
    for attempt in range(retries):
        try:
            consumer = KafkaConsumer(topic,
                bootstrap_servers=bootstrap_server,
                group_id=group_id,
                auto_offset_reset="earliest",
                enable_auto_commit=False,
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))
            )
            if consumer.bootstrap_connected():
                logging.info(f'Connected to Kafka broker at {bootstrap_server}')
                return consumer
        except NoBrokersAvailable:
            logging.warning(f'Kafka broker at {bootstrap_server} unavailable (attempt {attempt+1}/{retries})')
            time.sleep(delay)

    logging.error(f'Failed to connect to Kafka broker at {bootstrap_server} after {retries} attempts')
    exit(1)


def init_kafka_producer(bootstrap_server: str, retries: int = 5, delay: int = 5) -> KafkaProducer:
    for attempt in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_server,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            if producer.bootstrap_connected():
                logging.info(f'Connected to Kafka broker at {bootstrap_server}')
                return producer

        except NoBrokersAvailable:
            logging.warning(f'Kafka broker at {bootstrap_server} unavailable (attempt {attempt+1}/{retries})')
            time.sleep(delay)

    logging.error(f'Failed to connect to Kafka broker at {bootstrap_server} after {retries} attempts')
    exit(1)