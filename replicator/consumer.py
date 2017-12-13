# consumer
import json
import time
import sqlite3
import os
import re
import logging
from tqdm import tqdm
from mykafka import get_consumer

logging.basicConfig(filename='consumer.log', level=logging.INFO)


def _get_connection():
    conn = sqlite3.connect('dos.db')

    return conn


def add_object_to_repo(data_object, conn):
    conn.execute('INSERT INTO dos VALUES (?, ?)', (data_object['id'], data_object['created']))
    conn.commit()


def setup_repo():
    try:
        os.remove('dos.db')
    except FileNotFoundError:
        pass

    conn = sqlite3.connect('dos.db')

    conn.execute('''CREATE TABLE IF NOT EXISTS dos (id text, created text)''')
    conn.commit()
    conn.close()


def start_replication(consumer, connection):
    print('Starting replication')
    i, j = 0, 0

    start = time.time()
    with tqdm(total=538) as progress_bar:
        for msg in consumer:
            i += 1
            if msg.key.startswith(b'do:'):
                j += 1
                logging.info('Got do %s --> %s', msg.key, msg.value)
                do = json.loads(msg.value.decode('ascii'))
                add_object_to_repo(data_object=do, conn=connection)
                progress_bar.update()
            if msg.key.startswith(b'file:'):
                fname = msg.key.decode('ascii')[5:]
                dirname = fname.split('/')[0]
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                gg = re.search(r'\.\d+$', fname)
                if gg is not None:
                    fname = fname[:gg.start()]

                logging.info('Got file %s --> %s', fname, msg.value[:20])
                with open(fname, 'ab+') as f:
                    f.write(msg.value)

    end = time.time()

    logging.info('Replication finished: Got %s messages and %s objects', i, j)
    logging.info('Elapsed time %.3f', (end - start))


if __name__ == "__main__":
    setup_repo()
    c = get_consumer()
    connection = _get_connection()
    start_replication(c, connection)
    connection.close()
