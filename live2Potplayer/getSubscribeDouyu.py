import configparser
import json
import os
import shutil
import time
import urllib.request
from urllib.request import urlretrieve

import PIL.Image as im
import pyperclip
import pythoncom
import requests
from win32com.shell import shell, shellcon


def downloadfile(url,filename):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/51.0.    2704.103 Safari/537.36"}
    request = urllib.request.Request(url,headers = headers)
    try:
        response = urllib.request.urlopen(url)
    except:
        print('ERROR:Cannot download '+url)
        return False
    else:
        with open(filename,'wb') as f:
                f.write(response.read())
        return True

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(os.path.split(os.path.realpath(__file__))[0] + '\\config.ini')
    persist = config.get('baseconf', 'persist')
    dir = config.get('baseconf', 'dir')
    python = persist + '\\shims\\python.exe'
    script = dir + '\\douyu2potplayer.py'

    commits = 'https://api.github.com/repos/wbt5/real-url/commits'
    session = requests.session()
    result = session.get(commits).text
    result = json.loads(result)
    print(result[0]['sha'])
    with open('sha.txt', 'r') as file:
        sha = file.read()
    if sha != result[0]['sha']:
        with open(dir + '//sha.txt', 'w') as file:
            sha = file.write(result[0]['sha'])
            link = 'https://codeload.github.com/wbt5/real-url/zip/refs/heads/master'
            while True:
                if downloadfile(link, 'tmp.zip'):
                    break
            try:
                shutil.rmtree('lib')
            except:
                pass
            os.system('7z x tmp.zip')
            os.remove('tmp.zip')
            os.rename('real-url-master', 'lib')
    os.system('start msedge "https://www.douyu.com/wgapi/livenc/liveweb/follow/list?sort=0&cid1=0"')
    last_string = pyperclip.paste()
    while True:
        time.sleep(0.2)
        string = pyperclip.paste()
        if string != last_string and string != '':
            rawResult = json.loads(string)
            break
    for item in rawResult['data']['list']:
        nickname = item['nickname']
        roomID = item['room_id']
        figure = item["avatar_small"]
        urlretrieve(figure, dir + '//image//' + str(roomID) + '.jpg')
        a=im.open(dir + '//image//' + str(roomID) + '.jpg')
        a.save(dir + '//image//' + str(roomID) + '.ico')
        os.remove(dir + '//image//' + str(roomID) + '.jpg')
        with open(dir + '//live/' + str(roomID) + '.vbs', 'w') as file:
            file.write('set ws=WScript.CreateObject("WScript.Shell")\n')
            file.write('ws.Run "' + python.replace('\\', '\\\\') + ' ' + script.replace('\\', '\\\\') + ' ' + str(roomID) + '", 0')
        try:
            filename = dir + "\\live\\" + str(roomID) + '.vbs'  # 要创建快捷方式的文件的完整路径
            iconname = dir + "\\image\\" + str(roomID) + '.ico'
            lnkname = os.environ["appdata"] + r"\\Microsoft\\Windows\\Start Menu\\Programs\\Scoop Apps\\live\\斗鱼直播-" + nickname + '.lnk'

            shortcut = pythoncom.CoCreateInstance(
                shell.CLSID_ShellLink, None,
                pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
            shortcut.SetPath(filename)

            shortcut.SetWorkingDirectory("E:\\Project\\GitHub\\real-url") # 设置快捷方式的起始位置, 不然会出现找不到辅助文件的情况
            shortcut.SetIconLocation(iconname, 0)  # 可有可无，没有就默认使用文件本身的图标
            if os.path.splitext(lnkname)[-1] != '.lnk':
                lnkname += ".lnk"
            shortcut.QueryInterface(pythoncom.IID_IPersistFile).Save(lnkname, 0)

        except Exception as e:
            print(e.args)
