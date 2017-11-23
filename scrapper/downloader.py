import requests
from multiprocessing import Pool
import logging
import shutil
import os

logging.basicConfig(filename='downloading.log', level=logging.DEBUG)


def download_file(args, **kwargs):
    url = args[1]
    pid = args[0]
    fname = args[2]

    os.makedirs(pid, exist_ok=True)
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        logging.warning('Problem processing: {}/{} from {}'.format(pid, fname, url))
    with open(os.path.join(pid, fname), 'wb') as f:
        shutil.copyfileobj(r.raw, f)
        logging.info('Downloading completed {}'.format(url))


def get_items():
    with open('file.list', 'r') as f:
        fnr = 0
        for l in f:
            pid, url, fname = l.split(' ', 2)
            yield pid, url, fname
            fnr += 1


if __name__ == "__main__":
    print('Starting')
    with Pool(15) as p:
        p.map(download_file, get_items())
