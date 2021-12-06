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
    # with open(os.path.split(os.path.realpath(__file__))[0] + '\\tmp.log', 'w') as file:
    #     file.write(url)
    try:
        domain = re.search(r'(http://.+?)/emby', url).group(1)
    except:
        domain = re.search(r'(https://.+?)/emby', url).group(1)
    session = requests.session()
    response = session.get(domain + '/emby/users?api_key=' + token, proxies={'http': None, 'https': None})
    for item in response.json():
        if item['Name'] == userName:
            userId = item['Id']
            break
    url = url.replace('emby://', '').replace('%20', ' ')
    config1= configparser.RawConfigParser()
    config1.optionxform = lambda option: option
    config1.read(persist + '\\apps\\potplayer\\current\\PotPlayer64.ini', encoding="utf-16")
    config1.remove_option('Settings', 'VideoRen2')
    config1.write(open(persist + '\\apps\\potplayer\\current\\PotPlayer64.ini', "w", encoding="utf-16"), space_around_delimiters=False)
    os.system(persist + '\\apps\\potplayer\\current\\PotPlayer64.exe "' + url + '"')
    with open(persist + '\\persist\\potplayer\\Playlist\\PotPlayer64.dpl', 'r', encoding='utf-8-sig') as file:
        content = file.read()
        playtime = int(re.search(r'playtime=(\d+)', content).group(1))
        endtime = int(re.search(r'1\*duration2\*(\d+)', content).group(1))
    tmp = url.split(' ')
    tmp = tmp[0]
    item = tmp.split('/')[5]
    if endtime - playtime > 180000:
        response = session.post(domain + '/emby/users/' + userId + '/Items/' + item + '/UserData?api_key=' + token, data = {'PlaybackPositionTicks': playtime * 10000}, proxies={'http': None, 'https': None})
        print(response)
    else:
        response = session.post(domain + '/emby/Users/' + userId + '/PlayedItems/' + item + '?api_key=' + token, proxies={'http': None, 'https': None})
        print(response)
    
