# consumer
import json
import time
from mykafka import get_consumer
import sqlite3
import os
import re
from tqdm import tqdm
import logging

logging.basicConfig(filename='consumer.log', level=logging.INFO)


def _get_connection():
    conn = sqlite3.connect('dos.db')

    return conn


def add_object_to_repo(do, conn):
    conn.execute('INSERT INTO dos VALUES (?, ?)', (do['id'], do['created']))
    conn.commit()


def setup_repo():
    try:
        os.remove('dos.db')
    except:
        pass

    conn = sqlite3.connect('dos.db')

    conn.execute('''CREATE TABLE IF NOT EXISTS dos (id text, creted text)''')
    conn.commit()
    conn.close()


def start_replication():
    objects = dict()
    print('Starting replication')
    setup_repo()
    c = get_consumer()
    connection = _get_connection()
    i, j = 0, 0

    start = time.time()
    with tqdm(total=538) as bar:
        for msg in c:
            i += 1
            if msg.key.startswith(b'do:'):
                j += 1
                logging.info('Got do {} --> {}'.format(msg.key, msg.value))
                do = json.loads(msg.value.decode('ascii'))
                objects[do['id']] = do
                add_object_to_repo(do=do, conn=connection)
                bar.update()
            if msg.key.startswith(b'file:'):
                fname = msg.key.decode('ascii')[5:]
                dirname = fname.split('/')[0]
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                gg = re.search(r'\.\d+$', fname)
                if gg is not None:
                    fname = fname[:gg.start()]

                logging.info('Got file {} --> {}'.format(fname, msg.value[:20]))
                with open(fname, 'ab+') as f:
                    f.write(msg.value)

    end = time.time()

    msg = 'Replication finished: Got {} messages and {} objects'.format(i, j)
    print(msg)
    logging.info(msg)

    msg = 'Elapsed time {0:.2f}'.format(end - start)
    print(msg)
    logging.info(msg)

    with open('objects.json', 'w+') as f:
        json.dump(objects, f)


if __name__ == "__main__":
    start_replication()
