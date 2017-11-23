# docker run -it --rm -p 8080:8080 --link b2kafka_kafka_1:kafka --link b2kafka_zookeeper_1:zookeeper --volume /Users/jj/git/b2kafka/:/app/ uploader:latest /bin/bash

from flask import Flask, render_template, jsonify
from flask_bootstrap import Bootstrap
from multiprocessing import Process
from repo import get_single_object, get_file_list, get_do, setup_repo, add_object_to_repo, prefix
import os
import json
from time import sleep, time as tmp

import sys
sys.path.append('..')
from mykafka import get_consumer

app = Flask(__name__)
Bootstrap(app)


def fake_replication():
    print('Starting fake replication')
    setup_repo()

    with open('./out.json', 'r') as f:
        dos = json.load(f)

    for do in dos:
        add_object_to_repo(do)
        sleep(.3)

    print('Replication finished')


def start_replication():
    print('Starting replication')
    setup_repo()
    consumer = get_consumer()
    i, j = 0, 0

    start = tmp()

    for msg in consumer:
        i += 1
        if msg.key.startswith(b'do:'):
            j += 1
            print('Got do {} --> {}'.format(msg.key, msg.value))
            do = json.loads(msg.value.decode('ascii'))
            add_object_to_repo(do)
        if msg.key.startswith(b'file:'):
            fname = msg.key.decode('ascii')[5:]
            dirname = fname.split('/')[0]
            if not os.path.exists(os.path.join(prefix, dirname)):
                os.makedirs(os.path.join(prefix, dirname))

            print('Got file {} --> {}'.format(fname, msg.value[:30]))
            with open(os.path.join(prefix, fname), 'wb+') as f:
                f.write(msg.value)
    end = tmp()

    print('Replication finished: Got {} messages and {} objects'.format(i, j))
    print('Elapsed time {0:.2f}'.format(end - start))


@app.before_first_request
def setup():
    p = Process(target=start_replication)
    p.start()


@app.route('/data/', methods=['GET'])
def get_data():
    return jsonify({'length': len(list(get_do()))})


@app.route('/object/<ids>', methods=['GET'])
def get_single(ids):
    obj = get_single_object(ids)
    return render_template('single.html', obj=obj, filelist=get_file_list(ids))


@app.route('/', methods=['GET'])
def index():
    data = list(get_do())
    return render_template('index.html', data=data)


# from flask import appcontext_tearing_down
# appcontext_tearing_down.connect(join_thread, app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
