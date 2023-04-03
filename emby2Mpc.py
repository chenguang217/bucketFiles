import configparser
import os
import re
import sys
import time
import threading

import requests
import datetime

episodes = []
record = []


class myconf(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr

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
                response = session.get(domain + '/emby/Users/' + userId + '/Items?Ids=' + item + '&api_key=' + token, proxies={'http': None, 'https': None}, verify = False)
                response = session.post(domain + '/emby/users/' + userId + '/Items/' + item + '/UserData?api_key=' + token, data = {'PlaybackPositionTicks': duration * 10000, 'Played': response.json()['Items'][0]['UserData']['Played'], "LastPlayedDate": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.0000000+00:00")}, proxies={'http': None, 'https': None}, verify = False)
            elif state == 'Finished':
                response = session.post(domain + '/emby/Users/' + userId + '/PlayedItems/' + item + '?api_key=' + token, proxies={'http': None, 'https': None}, verify = False)

def accessSub(url):
    response = requests.get(url, proxies={'http': None, 'https': None}, verify = False)

def start():
    os.system(persist + '\\apps\\mpc-be\\current\\mpc-be64.exe /play')

def dmitriRender(flag):
    config = myconf()
    config.read(persist + '\\apps\\mpc-be\\current\\mpc-be64.ini', encoding='utf-8-sig')
    if flag:
        config.set('ExternalFilters\\000', 'Enabled', '1')
    else:
        config.set('ExternalFilters\\000', 'Enabled', '0')
    config.write(open(persist + '\\apps\\mpc-be\\current\\mpc-be64.ini', "w", encoding='utf-8-sig'), space_around_delimiters=False)

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(os.path.split(os.path.realpath(__file__))[0] + '\\config.ini')
    token = config.get('baseconf', 'token')
    userName = config.get('baseconf', 'userName')
    persist = config.get('baseconf', 'persist')
    ifDmitri = config.get('baseconf', 'dmitriRender')
    url = sys.argv[1]
    try:
        domain = re.search(r'(http://.+?)/emby', url).group(1)
    except:
        domain = re.search(r'(https://.+?)/emby', url).group(1)
    session = requests.session()
    response = session.get(domain + '/emby/users?api_key=' + token, proxies={'http': None, 'https': None}, verify = False)
    for item in response.json():
        if item['Name'] == userName:
            userId = item['Id']
            break
    url = url.replace('emby://', '').replace('%20', ' ')
    parameter = url.split(' ')
    target = parameter[0]
    position = parameter[3].replace('/seek=', '')
    if len(position.split(':')) == 2:
        position = '00:' + position
    if len(parameter[1].replace('/sub=', '')) == 0:
        sub = ''
    else:
        sub = ' /sub "' + parameter[1].replace('/sub=', '') + '"'
    with open(persist + '\\persist\\mpc-be\\history.mpc_lst', 'w', encoding='utf_8_sig') as file:
        file.write('; MPC-BE History File 0.1\n\n[001]\nPath=' + target + '\n' + 'Title=' + re.search(r'/(stream.+?)\?api_key', target).group(1) + '\n' + 'Position=' + position + '\n')
    with open(persist + '\\persist\\mpc-be\\Default.mpcpl', 'w', encoding='utf-8') as file:
        file.write('MPCPLAYLIST\naudio,-1\nsubtitles,-1\n1,type,0\n')
        itemId = url.split('/')[5]
        response = requests.get(domain + '/emby/Items?Ids=' + itemId + '&api_key=' + token, proxies={'http': None, 'https': None}, verify = False)
        file.write('1,label,' + response.json()['Items'][0]['Name'] + '\n1,filename,' + target + '\n')
        if ifDmitri == 'true':
            response = requests.get(domain + '/emby/Items/' + itemId + '/PlaybackInfo?api_key=' + token, proxies={'http': None, 'https': None}, verify = False)
            frameRate = response.json()['MediaSources'][0]['MediaStreams'][0]['AverageFrameRate']
            if frameRate >= 60:
                # disable dmitriRender
                dmitriRender(False)
            else:
                # enable dmitriRender
                dmitriRender(True)
        if len(parameter[1].replace('/sub=', '')) != 0:
            file.write('1,subtitle,' + parameter[1].replace('/sub=', '') + '\n')
        episodes.append(url.split(' ')[0])
        i = 2
        try:
            seriesId = response.json()['Items'][0]['SeriesId']
            seasonId = response.json()['Items'][0]['SeasonId']
            response = requests.get(domain + '/emby/Shows/' + seriesId + '/Episodes?SeasonId=' + seasonId + '&StartItemId=' + itemId + '&api_key=' + token, proxies={'http': None, 'https': None}, verify = False)
            for item in response.json()['Items']:
                if item['Id'] == itemId:
                    continue
                response = requests.get(domain + '/emby/Items/' + item['Id'] + '/PlaybackInfo?api_key=' + token, proxies={'http': None, 'https': None}, verify = False)
                Container = response.json()['MediaSources'][0]['Container']
                episode = domain + '/emby/videos/' + item['Id'] + '/stream.' + Container + '?Static=true&api_key=' + token
                response = requests.get(domain + '/emby/Users/' + userId + '/Items/' + item['Id'] + '?&api_key=' + token, proxies={'http': None, 'https': None}, verify = False)
                ifSub = False
                ifExternal = False
                # print(response.json()["MediaSources"][0]['DefaultSubtitleStreamIndex'])
                for media in response.json()["MediaSources"][0]['MediaStreams']:
                    if media["Type"] == "Subtitle":
                        if 'DisplayLanguage' in media.keys():
                            if media['Index'] == response.json()["MediaSources"][0]['DefaultSubtitleStreamIndex'] and media['DisplayLanguage'] == 'Chinese Simplified':
                                print('selected chinese subtitle')
                                path = media['Codec']
                                ifSub = True
                                index = media['Index']
                            elif media['Index'] == response.json()["MediaSources"][0]['DefaultSubtitleStreamIndex'] and media['IsExternal']:
                                path = media['Codec']
                                ifSub = True
                                ifExternal = True
                                index = media['Index']
                            elif media['IsExternal'] and not ifExternal:
                                path = media['Codec']
                                ifSub = True
                                index = media['Index']
                            elif media['DisplayLanguage'] == 'Chinese Simplified':
                                path = media['Codec']
                                ifSub = True
                                index = media['Index']
                        else:
                            if media['Index'] == response.json()["MediaSources"][0]['DefaultSubtitleStreamIndex'] and media['IsExternal']:
                                path = media['Codec']
                                ifSub = True
                                ifExternal = True
                                index = media['Index']
                            elif media['IsExternal'] and not ifExternal:
                                path = media['Codec']
                                ifSub = True
                                index = media['Index']
                if ifSub:
                    subtitle = domain + '/emby/videos/' + item['Id'] + '/' + response.json()['MediaSources'][0]['Id'] + '/Subtitles/' + str(index) + '/Stream.' + path + '?api_key=' + token
                    thread = threading.Thread(target=accessSub, args=(subtitle,))
                    record.append(thread)
                else:
                    subtitle = ''
                file.write(str(i) + ',type,0\n' + str(i) + ',label,' + item['Name'] + '\n' + str(i) + ',filename,' + episode + '\n')
                if ifSub:
                    file.write(str(i) + ',subtitle,' + subtitle + '\n')
                i += 1
                episodes.append(episode)
        except:
            pass
    thread2 = threading.Thread(target=start)
    thread2.start()
    for thread in record:
        thread.setDaemon(True)
        thread.start()
    thread2.join()
    Mark(episodes)
    with open(persist + '\\persist\\mpc-be\\history.mpc_lst', 'w', encoding='utf-8') as file:
        pass
