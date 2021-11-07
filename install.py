import os
import sys

import rarfile
import requests
import zipfile

def getCookie(cookie_string):
    cookie_string = cookie_string.strip('\n').strip()
    cookie_list = cookie_string.split(';')
    cookie_new_list = [i.strip('\n').strip() for i in cookie_list]
    cookie_dict = {}
    for ck in cookie_new_list:
        if '=' in ck:
            # 如果有两个=，那么只选最左边的切
            ck_list = ck.split('=', 1)
            cookie_dict[ck_list[0]] = ck_list[1]
    return cookie_dict

if __name__ == "__main__":
    os.chdir(sys.argv[1])
    if 'http' in sys.argv[2]:
        os.system('wget -O tmp.zip "' + sys.argv[2] + '"')
        os.system('7z x tmp.zip')
        file = rarfile.RarFile('tmp.zip')
        for f in file.infolist():
            dir = f.filename.split('/')[0]
            break
        os.system('mv ' + dir + '/* ./')
        os.removedirs(dir)
        os.remove('tmp.zip')
    elif 'adycloud' in sys.argv[2]:
        linkId = sys.argv[2].split('/')[1]
        response = session.put('https://pan.adycloud.com/api/v3/share/download/' + linkId)
        link = response.json()['data']
        os.system('wget -O tmp.zip "' + link + '"')
        os.system('7z x tmp.zip')
        file = zipfile.ZipFile('tmp.zip')
        for f in file.infolist():
            dir = f.filename.split('/')[0]
            break
        os.system('mv ' + dir + '/* ./')
        os.removedirs(dir)
        os.remove('tmp.zip')
    else:
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
        cookies = input('输入和彩云cookies: ')
        cookies = getCookie(cookies)
        response = session.post(url, headers=headers, data=data, cookies=cookies)
        text = response.json()
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
