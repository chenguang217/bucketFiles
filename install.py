import os
import sys
import time
import re

import requests
from lxml import etree
from requests.models import Response
import rarfile
import shutil

if __name__ == "__main__":
    os.chdir(sys.argv[1])
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37'}
    linkId = sys.argv[2]
    passId = sys.argv[3]
    url = 'https://caiyun.139.com/stapi/outlink/info'
    data = {
        'linkId': linkId,
        'path': 'root',
        'start': 1,
        'end': 15,
        'sortType': 0,
        'sortDr': 1,
        'pass': passId
    }
    session = requests.session()
    response = session.post(url, headers=headers, data=data)
    text = response.json()
    url = 'https://caiyun.139.com/stapi/outlink/content/download'
    contentIds = text['data']['pCaID'] + '/' + text['data']['coLst']['outLinkCoInfo']['coID']
    data = {
        'linkId': linkId,
        'contentIds': contentIds
    }
    response = session.post(url, headers=headers, data=data)
    text = response.json()
    print(text)
    link = text['data']['redrUrl']
    os.system('wget -O tmp.zip "' + link + '"')
    os.system('7z x tmp.zip')
    file = rarfile.RarFile('tmp.zip')
    for f in file.infolist():
        dir = f.filename.split('/')[0]
        break
    os.system('mv ' + dir + '/* ./')
    os.removedirs(dir)
    os.remove('tmp.zip')