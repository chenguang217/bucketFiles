import configparser
import multiprocessing
import os
import re
import subprocess
import sys
import time

import requests
from pykeyboard import *

episodes = []
PID = ''

def d11():
    time.sleep(5)
    k = PyKeyboard()
    k.press_key(k.alt_key)
    k.press_key(k.control_key)
    k.tap_key(k.function_keys[6])
    k.release_key(k.alt_key)
    k.release_key(k.control_key)

def appends(url, token, domain, userId, persist):
    time.sleep(3)
    itemId = url.split('/')[7]
    response = requests.get(domain + '/emby/Items?Ids=' + itemId + '&api_key=' + token)
    global PID
    try:
        seriesId = response.json()['Items'][0]['SeriesId']
        seasonId = response.json()['Items'][0]['SeasonId']
        response = requests.get(domain + '/emby/Shows/' + seriesId + '/Episodes?SeasonId=' + seasonId + '&StartItemId=' + itemId + '&api_key=' + token)
        for item in response.json()['Items']:
            if item['Id'] == itemId:
                continue
            response = requests.get(domain + '/emby/Items/' + item['Id'] + '/PlaybackInfo?api_key=' + token)
            Container = response.json()['MediaSources'][0]['Container']
            episode = domain + '/emby/videos/' + item['Id'] + '/stream.' + Container + '?Static=true&api_key=' + token
            response = requests.get(domain + '/emby/Users/' + userId + '/Items/' + item['Id'] + '?&api_key=' + token)
            ifSub = False
            for media in response.json()["MediaSources"][0]['MediaStreams']:
                if media["Type"] == "Subtitle":
                    try:
                        path = media["Path"]
                        ifSub = True
                        index = media["Index"]
                    except:
                        pass
            if ifSub:
                subtitle = domain + '/emby/videos/' + item['Id'] + response.json()['MediaSources'][0]['Id'] + '/Subtitles/' + str(index) + '/Stream.' + path.split('.')[-1] + '?api_key=7753ae02845a4e968eeb39aca46c03e3'
            else:
                subtitle = ''
            for line in os.popen('tasklist /V /FI "IMAGENAME eq PotPlayer64.exe"').readlines():
                if r'PotPlayer64.exe' in line:
                    if 'stream' in line:
                        print(line)
                        os.system(persist + '\\apps\\potplayer\\current\\PotPlayer64.exe "' + episode + '" /sub="' + subtitle + '" /add')
            episodes.append(episode)
            print(episode)
            time.sleep(1)
    except:
        pass

t = multiprocessing.Process(target=d11)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(os.path.split(os.path.realpath(__file__))[0] + '\\config.ini')
    token = config.get('baseconf', 'token')
    userName = config.get('baseconf', 'userName')
    persist = config.get('baseconf', 'persist')
    url = sys.argv[1]
    episodes.append(url.replace('emby://', '').replace('%20', ' '))
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
    t2 = multiprocessing.Process(target=appends, args=(url, token, domain, userId, persist,))
    url = url.replace('emby://', '').replace('%20', ' ')
    if 'hdr' in url:
        config1= configparser.RawConfigParser()
        config1.optionxform = lambda option: option
        config1.read(persist + '\\apps\\potplayer\\current\\PotPlayer64.ini', encoding="utf-16")
        config1.set('Settings', 'VideoRen2', '15')
        subprocess.Popen(persist + '\\apps\\emby2potplayer\\current\\HDRSwitch.exe')
        config1.write(open(persist + '\\apps\\potplayer\\current\\PotPlayer64.ini', "w", encoding="utf-16"), space_around_delimiters=False)
    else:
        config1= configparser.RawConfigParser()
        config1.optionxform = lambda option: option
        config1.read(persist + '\\apps\\potplayer\\current\\PotPlayer64.ini', encoding="utf-16")
        config1.remove_option('Settings', 'VideoRen2')
        config1.write(open(persist + '\\apps\\potplayer\\current\\PotPlayer64.ini', "w", encoding="utf-16"), space_around_delimiters=False)
        t.start()
    url = url.replace(' hdr', '')
    time.sleep(1.5)
    t2.start()
    os.system(persist + '\\apps\\potplayer\\current\\PotPlayer64.exe "' + url + '"')
    t2.terminate()
    os.system('taskkill /F /IM HDRSwitch.exe')
    os.system('taskkill /F /IM PotPlayer64.exe')
    with open(persist + '\\persist\\potplayer\\Playlist\\PotPlayer64.dpl', 'r', encoding='utf-8-sig') as file:
        content = file.read()
        playList = []
        for i in range(len(episodes)):
            playList.append(re.search(str(i + 1) + r'\*file\*(.+?)\n', content))
        for i in range(len(episodes)):
            if playList[i] != None:
                state = 'Unknown'
                try:
                    endtime = int(re.search(str(i + 1) + r'\*duration2\*(\d+)', content).group(1))
                    try:
                        playtime = int(re.search(str(i + 1) + r'\*start\*(\d+)', content).group(1))
                        if endtime - playtime > 180000:
                            state = 'Progress'
                            duration = playtime
                        else:
                            state = 'Finished'
                    except:
                        playtime = re.search(str(i + 1) + r'\*played\*(\d)', content)
                        if playtime != None:
                            state = 'Finished'
                except:
                    state = 'UnPlayed'
                item = episodes[i].split('/')[5]
                if state == 'Progress':
                    response = session.post(domain + '/emby/users/' + userId + '/Items/' + item + '/UserData?api_key=' + token, data = {'PlaybackPositionTicks': duration * 10000}, proxies={'http': None, 'https': None})
                elif state == 'Finished':
                    response = session.post(domain + '/emby/Users/' + userId + '/PlayedItems/' + item + '?api_key=' + token, proxies={'http': None, 'https': None})
                print(response.text)
