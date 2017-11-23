import json
import requests
import os

base_url = os.getenv('B2SHARE_URL', 'https://b2share.eudat.eu/api/records')

creds = {
    'access_token': os.getenv('B2SHARE_TOKEN', None)
}
# 100 is the maximum value (higher values will be truncated at the server)
PAGE_SIZE = 100


def retrieve_items(page=1):
    params = dict()
    params.update(creds)
    pagination = {'size': PAGE_SIZE, 'page': page}
    params.update(pagination)

    r = requests.get(url=base_url, params=params)
    content = dict()
    try:
        content = r.json()['hits']['hits']
    except:
        print('Something went wrong: ')
        print(r.url)
        print(r.json())

    print('%d retrieved, elapsed time %s' % (len(content),
                                             r.elapsed))

    if len(content) != 0:
        print('There might be next page!')
        content = content + retrieve_items(page + 1)

    return content


def process_flist():
    for rec in finfo['contents']:
        furl = rec['links']['self']
        fname = rec['key']


def extract_file_lists(hits):
    for record in hits:
        if not 'files' in record['links']:
            continue

        url = record['links']['files']
        finfo = requests.get(url)
        if finfo.status_code != 200:
            print('Got bad code')
            continue

        finfo = finfo.json()

        if not 'contents' in finfo:
            print('No contents here')
            continue

        yield record['id'], finfo['contents']


def procesor():
    with open('out.json', 'r') as f:
        hits = json.load(f)

    cnt = dict()
    for rid, rlist in extract_file_lists(hits):
        cnt[rid] = rlist

    return cnt


if __name__ == "__main__":
    if 'B2SHARE_TOKEN' not in os.environ:
        print('To retrieve remote records, provide access token in ' \
              'B2SHARE_TOKEN environment ' \
              'variable')
        exit(-1)

    items = retrieve_items(page=1)
    fname = 'out.json'
    print('Retrieved %d writing to %s' % (len(items), fname))
    with open(fname, 'w+') as f:
        json.dump(items, f)
