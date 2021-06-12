import os
import re
import sys

import requests
import configparser

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(os.path.split(os.path.realpath(__file__))[0] + '\\config.ini')
    token = config.get('baseconf', 'token')
    userName = config.get('baseconf', 'userName')
    persist = config.get('baseconf', 'persist')
    url = sys.argv[1]
    try:
        domain = re.search(r'(http://.+)/emby', url).group(1)
    except:
        domain = re.search(r'(https://.+)/emby', url).group(1)
    session = requests.session()
    response = session.get(domain + '/emby/users?api_key=' + token, proxies={'http': None, 'https': None})
    for item in response.json():
        if item['Name'] == userName:
            userId = item['Id']
            break
    url = url.replace('emby://', '').replace('%20', ' ')
    os.system(persist + '\\apps\\potplayer\\current\\PotPlayerMini64.exe "' + url + '"')
    with open(persist + '\\persist\\potplayer\\Playlist\\PotPlayerMini64.dpl', 'r', encoding='utf-8-sig') as file:
        content = file.read()
        playtime = int(re.search(r'playtime=(\d+)', content).group(1))
    tmp = url.split(' ')
    tmp = tmp[0]
    item = tmp.split('/')[5]
    response = session.post(domain + '/emby/users/' + userId + '/Items/' + item + '/UserData?api_key=' + token, data = {'PlaybackPositionTicks': playtime * 10000}, proxies={'http': None, 'https': None})
    print(response)
