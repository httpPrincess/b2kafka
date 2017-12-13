#!/usr/bin/env python3
import sys
import os
from kafka import KafkaConsumer, KafkaProducer

TOPIC = 'b2share'
PARTITION_NUMBER = 1
DEBUG = bool(os.getenv('DEBUG', 'False'))
# with 40 MB chunk size we get 95% of DOs
MAX_SIZE = 40000000
# 5 * 1024 * 1024
CHUNK_SIZE = MAX_SIZE


def get_address():
    server = os.getenv('KAFKA_PORT_129092_TCP_ADDR', 'localhost')
    port = os.getenv('KAFKA_PORT_219092_TCP_PORT', '29092')
    return server + ':' + port


def get_producer():
    return KafkaProducer(bootstrap_servers=get_address(), max_request_size=20 * MAX_SIZE,
                         compression_type=None, batch_size=65535, request_timeout_ms=100000,
                         buffer_memory=10 * 33554432, max_block_ms=10 * 60000)


def get_consumer():
    return KafkaConsumer(TOPIC, auto_offset_reset='earliest',
                         bootstrap_servers=get_address())


def _publish(key, value):
    producer = get_producer()
    future = producer.send(TOPIC, key=key, value=value)
    future.get()
    print('Uploading {}({}) --> {}'.format(key, len(value), value[:10]))
    producer.flush()
    producer.close()



if __name__ == "__main__":
    file_name = ''
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        print('Provide file name to upload')

    print('Uploading %s' % file_name)
    with open(file_name, 'rb') as file:
        chunk_nr = 0
        while True:
            chunk = file.read(CHUNK_SIZE)
            if chunk:
                _publish(bytes('file:{}.{}'.format(file_name, chunk_nr), 'ascii'), chunk)
                chunk_nr += 1
            else:
                break
