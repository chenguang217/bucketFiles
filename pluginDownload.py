import os
import time
import requests
import xmltodict
import configparser
import urllib.request
import zipfile

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
    appDir = config.get('baseconf', 'dir')
    for i in range(5):
        try:
            response = requests.get('https://dldir1.qq.com/weixin/Windows/XPlugin/updateConfigWin.xml', proxies={'http': None, 'https': None}, verify = False)
        except:
            response = 0
        if response != 0:
            break
        time.sleep(1)
    content_dict = xmltodict.parse(response.text)
    plugins = content_dict['updateConfig']['Versions']['VersionInfo']
    for plugin in plugins:
        keys = list(plugin.keys())
        if keys[0] == '@appClientVerMin' and keys[1] == '@fullurl':
            os.system('mkdir ' + os.path.join(persist + r"\WeChat\XPlugin\Plugins", plugin['@name'], plugin['@version'] + r"\extracted" ))
            for i in range(5):
                if downloadfile(plugin['@fullurl'], os.path.join(persist + r"\WeChat\XPlugin\Plugins", plugin['@name'], plugin['@version'] + r"\extracted\tmp.zip")):
                    break
            zFile = zipfile.ZipFile(os.path.join(persist + r"\WeChat\XPlugin\Plugins", plugin['@name'], plugin['@version'] + r"\extracted\tmp.zip"), "r")
            for fileM in zFile.namelist(): 
                zFile.extract(fileM, os.path.join(persist + r"\WeChat\XPlugin\Plugins", plugin['@name'], plugin['@version'] + r"\extracted"))
            zFile.close()
            os.remove(os.path.join(persist + r"\WeChat\XPlugin\Plugins", plugin['@name'], plugin['@version'] + r"\extracted\tmp.zip"))
        elif keys[0] == '@appClientVerMin' and keys[1] == '@deviceAbis' and plugin['@deviceAbis'] == 'x64|x86':
            os.system('mkdir ' + os.path.join(persist + r"\WeChat\XPlugin\Plugins", plugin['@name'], plugin['@version'] + r"\extracted" ))
            for i in range(5):
                if downloadfile(plugin['@fullurl'], os.path.join(persist + r"\WeChat\XPlugin\Plugins", plugin['@name'], plugin['@version'] + r"\extracted\tmp.zip")):
                    break
            zFile = zipfile.ZipFile(os.path.join(persist + r"\WeChat\XPlugin\Plugins", plugin['@name'], plugin['@version'] + r"\extracted\tmp.zip"), "r")
            for fileM in zFile.namelist(): 
                zFile.extract(fileM, os.path.join(persist + r"\WeChat\XPlugin\Plugins", plugin['@name'], plugin['@version'] + r"\extracted"))
            zFile.close()
            os.remove(os.path.join(persist + r"\WeChat\XPlugin\Plugins", plugin['@name'], plugin['@version'] + r"\extracted\tmp.zip"))
