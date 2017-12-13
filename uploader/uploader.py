# uploader to kafka

import json
import os
import datetime
import time
import sys
import logging
from tqdm import tqdm
from mykafka import _publish, MAX_SIZE, chunk_size


logging.basicConfig(filename='uploader.log', level=logging.INFO)


def upload_to_kafka(oid, data_object, files):
    files = list(map(lambda x: os.path.join(oid, x), files))
    data_object['files'] = files
    _publish(bytes('do:{}'.format(oid), 'ascii'), json.dumps(data_object).encode('ascii'))

    for current_file in files:
        fsize = os.stat(current_file).st_size
        with open(current_file, 'rb') as file:
            fname = current_file.replace('\\', '')
            fname = fname.replace('^J', '')
            fname = fname.replace('\n', '')
            fname = fname.replace('?', '')

            if fsize < MAX_SIZE:
                _publish(bytes('file:{}'.format(fname), 'ascii', errors='ignore'), file.read())
            else:
                chunk_nr = 0
                while True:
                    chunk = file.read(chunk_size)
                    if chunk:
                        _publish(bytes('file:{}.{}'.format(fname, chunk_nr), 'ascii', errors='ignore'), chunk)
                        chunk_nr += 1
                    else:
                        break


def get_files(oid):
    files = list()
    try:
        files = os.listdir(oid)
    except FileNotFoundError:
        pass

    return files


def process_list(hit_list, upload):
    i = 0
    start = time.time()
    total_files = 0

    for do in tqdm(hit_list):
        oid = do['id']
        if 'links' in do:
            do.pop('links')
        if 'files' in do:
            do.pop('files')

        files = get_files(oid)
        total_files += len(files)

        upload(oid, do, files)
        i += 1
    end = time.time()
    print('Uploaded objects: {}'.format(i))
    print('Uploaded files: {}'.format(total_files))
    print('Elapsed time: {}'.format(end - start))


if __name__ == "__main__":

    with open('out.json', 'r') as f:
        hits = json.load(f)

    hits = sorted(hits, key=lambda x: datetime.datetime.strptime(x['created'].split('.')[0], '%Y-%m-%dT%H:%M:%S'))

    resume = None
    if len(sys.argv) > 1:
        resume = sys.argv[1]

    if resume:
        print('Resuming from {}'.format(resume))
        idx = hits.index(next(i for i in hits if i['id'] == resume))
        if not idx:
            print('Unable to resume, id {} not found'.format(resume))
            exit(-1)

        hits = hits[idx:]

    process_list(hits, upload_to_kafka)
