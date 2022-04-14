import configparser
import os
import re
import subprocess
import sys
import threading
import time

import requests
import datetime

episodes = []


def appends(url, token, domain, userId, persist):
    time.sleep(3)
    itemId = url.split('/')[7]
    response = requests.get(domain + '/emby/Items?Ids=' + itemId + '&api_key=' + token)
    global episodes
    episodes.append(url.replace('emby://', '').replace('%20', ' ').split(' ')[0])
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
                subtitle = domain + '/emby/videos/' + item['Id'] + response.json()['MediaSources'][0]['Id'] + '/Subtitles/' + str(index) + '/Stream.' + path.split('.')[-1] + '?api_key=' + token
            else:
                subtitle = ''
            for line in os.popen('tasklist /V /FI "IMAGENAME eq mpc-be64.exe"').readlines():
                if r'mpc-be64.exe' in line:
                    if ' - MPC-BE x64 1.6.1' in line:
                        # print(line)
                        if ifSub:
                            os.system(persist + '\\apps\\mpc-be\\current\\mpc-be64.exe "' + episode + '" /sub "' + subtitle + '" /add')
                        else:
                            os.system(persist + '\\apps\\mpc-be\\current\\mpc-be64.exe "' + episode + '" /add')
            episodes.append(episode)
            # print(episodes)
            time.sleep(1)
    except:
        pass
        
def Mark(episodes):
    with open(persist + '\\persist\\mpc-be\\history.mpc_lst', 'r', encoding='utf-8') as file:
        content = file.read()
        playList = []
        for i in range(len(episodes)):
            state = 'Unknown'
            try:
                periodStart = content.index(episodes[i])
                try:
                    periodEnd = len(content[:periodStart]) + content[periodStart:].index('\n[') - 1
                except:
                    periodEnd = len(content) - 1
                progress = content[periodStart:periodEnd]
                playtime = re.search(r'Position=(.+?)\n', progress)
                if playtime == None:
                    state = 'Finished'
                else:
                    duration = playtime.group(1).split(':')
                    duration = int(duration[0]) * 3600 + int(duration[1]) * 60 + int(duration[2])
                    duration *= 1000
                    with open(persist + '\\persist\\mpc-be\\Default.mpcpl', 'r', encoding='utf-8') as file2:
                        content2 = file2.read()
                        periodEnd2 = content2.index(episodes[i])
                        periodStart2 = content2[:periodEnd2].rindex('time')
                        length = re.search(r'time,(.+?)\n', content2[periodStart2:periodEnd2]).group(1)
                        length = int(length.split(':')[0]) * 3600000 + int(length.split(':')[1]) * 60000 + int(length.split(':')[2]) * 1000
                    if length - duration > 180000:
                        state = 'Progress'
                    else:
                        state = 'Finished'
            except:
                state = 'UnPlayed'
            item = episodes[i].split('/')[5]
            print(state)
            if state == 'Progress':
                response = session.get(domain + '/emby/Users/' + userId + '/Items?Ids=' + item + '&api_key=' + token)
                response = session.post(domain + '/emby/users/' + userId + '/Items/' + item + '/UserData?api_key=' + token, data = {'PlaybackPositionTicks': duration * 10000, 'Played': response.json()['Items'][0]['UserData']['Played'], "LastPlayedDate": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.0000000+00:00")}, proxies={'http': None, 'https': None})
            elif state == 'Finished':
                response = session.post(domain + '/emby/Users/' + userId + '/PlayedItems/' + item + '?api_key=' + token, proxies={'http': None, 'https': None})


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(os.path.split(os.path.realpath(__file__))[0] + '\\config.ini')
    token = config.get('baseconf', 'token')
    userName = config.get('baseconf', 'userName')
    persist = config.get('baseconf', 'persist')
    url = sys.argv[1]
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
    t2 = threading.Thread(target=appends, args=(url, token, domain, userId, persist,))
    url = url.replace('emby://', '').replace('%20', ' ')
    t2.setDaemon(True)
    t2.start()
    parameter = url.split(' ')
    target = parameter[0]
    position = parameter[3].replace('/seek=', '')
    if len(position.split(':')) == 2:
        position = '00:' + position
    if len(position) == 0:
        position = ''
    else:
        position = ' /startpos ' + position
    if len(parameter[1].replace('/sub=', '')) == 0:
        sub = ''
    else:
        sub = ' /sub "' + parameter[1].replace('/sub=', '') + '"'
    os.system(persist + '\\apps\\mpc-be\\current\\mpc-be64.exe "' + target + '"' + position + sub)
    Mark(episodes)
    with open(persist + '\\persist\\mpc-be\\history.mpc_lst', 'w', encoding='utf-8') as file:
        pass
