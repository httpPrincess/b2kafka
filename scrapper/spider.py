import os
import json
import requests

base_url = os.getenv('B2SHARE_URL', 'https://b2share.eudat.eu/api/records')

credentials = {
    'access_token': os.getenv('B2SHARE_TOKEN', None)
}
# 100 is the maximum value (higher values will be truncated at the server)
PAGE_SIZE = 100


def retrieve_items(page=1):
    params = dict()
    params.update(credentials)
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

        if 'contents' not in finfo:
            print('No contents here')
            continue

        yield record['id'], finfo['contents']


def processor():
    with open('out.json', 'r') as f:
        hits = json.load(f)

    cnt = dict()
    for rid, rlist in extract_file_lists(hits):
        cnt[rid] = rlist

    return cnt


if __name__ == "__main__":
    if 'B2SHARE_TOKEN' not in os.environ:
        print('To retrieve remote records, provide access token in '
              'B2SHARE_TOKEN environment '
              'variable')
        exit(-1)

    items = retrieve_items(page=1)
    file_name = 'out.json'
    print('Retrieved %d writing to %s' % (len(items), file_name))
    with open(file_name, 'w+') as json_file:
        json.dump(items, json_file)
