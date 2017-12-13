from kafka import KafkaConsumer, KafkaProducer
import os
import logging

TOPIC = 'b2share'
PARTITION_NUMBER = 1
DEBUG = bool(os.getenv('DEBUG', 'False'))
# with 40 MB chunk size we get 95% of DOs
MAX_SIZE = 40000000
# 5 * 1024 * 1024
chunk_size = MAX_SIZE


def get_address():
    import os
    server = os.getenv('KAFKA_PORT_29092_TCP_ADDR', 'localhost')
    port = os.getenv('KAFKA_PORT_29092_TCP_PORT', '29092')
    return server + ':' + port


def get_producer():
    return KafkaProducer(bootstrap_servers=get_address(), max_request_size=20 * MAX_SIZE,
                         compression_type=None, batch_size=65535, request_timeout_ms=100000,
                         buffer_memory=10 * 33554432, max_block_ms=10 * 60000)


def get_consumer(client_id="1", group_id=None):
    return KafkaConsumer(TOPIC, auto_offset_reset='earliest',
                         bootstrap_servers=get_address(),
                         consumer_timeout_ms=100000,
                         client_id=client_id, group_id=group_id)
    # value_deserializer=lambda m: m[:500])


def _publish(key, value):
    producer = get_producer()
    future = producer.send(TOPIC, key=key, value=value)
    future.get()
    logging.info('Uploading {}({}) --> {}'.format(key, len(value), value[:10]))
    producer.flush()
    producer.close()
