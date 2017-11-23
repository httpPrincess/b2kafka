import os
import sqlite3
from flask import g

prefix = './data/'


def _get_connection():
    conn = g.get('_conn', None)
    if conn is None:
        conn = sqlite3.connect('dos.db')
        g._conn = conn

    return conn


def get_do():
    conn = _get_connection()
    for row in conn.execute('SELECT * FROM dos'):
        yield row


def get_single_object(ids):
    conn = _get_connection()
    return conn.execute('SELECT * FROM dos WHERE id==?', [ids, ]).fetchone()


def add_object_to_repo(do):
    conn = _get_connection()
    conn.execute('INSERT INTO dos VALUES (?, ?)', (do['id'], do['created']))
    conn.commit()


def get_file_list(ids):
    fl = list()
    try:
        fl = os.listdir(os.path.join(prefix, ids))
    except:
        pass

    return fl


def setup_repo():
    try:
        os.remove('dos.db')
    except:
        pass

    conn = sqlite3.connect('dos.db')

    conn.execute('''CREATE TABLE IF NOT EXISTS dos (id text, creted text)''')
    conn.commit()
    conn.close()
