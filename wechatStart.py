import os
import subprocess
import time
import psutil
import requests
import xmltodict
import configparser


def judgeprocess(processname):
    try:
        pl = psutil.pids()
        for pid in pl:
            if psutil.Process(pid).name() == processname:
                return 0
        else:
            return 1
    except:
        return 0

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(os.path.split(os.path.realpath(__file__))[0] + '\\config.ini')
    persist = config.get('baseconf', 'persist')
    appDir = config.get('baseconf', 'dir')
    state = 0
    times = 0
    wechat = appDir + r"\WeChat.exe"
    print(wechat)
    dir_list = set(sorted(os.listdir(os.environ.get("APPDATA") + r"\Tencent\WeChat\XPlugin\Plugins\WMPFRuntime"),  key=lambda x: os.path.getmtime(os.path.join(os.environ.get("APPDATA") + r"\Tencent\WeChat\XPlugin\Plugins\WMPFRuntime", x)), reverse=True))
    versionSet = set()
    for i in range(5):
        try:
            response = requests.get('https://dldir1.qq.com/weixin/Windows/XPlugin/updateConfigWin.xml', proxies={'http': None, 'https': None}, verify = False)
        except:
            response = 0
        print(response)
        if response != 0:
            break
        time.sleep(1)
    content_dict = xmltodict.parse(response.text)
    plugins = content_dict['updateConfig']['Versions']['VersionInfo']
    for plugin in plugins:
        if plugin['@name'] == 'WMPFRuntime':
            versionSet.add(plugin['@version'])
    for version in [version for version in versionSet if version not in dir_list]:
        try:
            os.system('mkdir ' + os.path.join(persist + r"\WeChat\XPlugin\Plugins\WMPFRuntime", version + r"\extracted" ))
            os.system(r'powershell.exe "New-Item -Type Junction -Path $env:APPDATA\Tencent\WeChat\XPlugin\Plugins\WMPFRuntime\\' + version + r'\extracted -Target ' + persist + r'\WeChat\XPlugin\Plugins\WMPFRuntime\\' + version + r'\extracted"')
        except:
            pass
    for version in [version for version in dir_list if version not in versionSet]:
        try:
            os.system(r"rmdir /S /Q " + persist + r"\WeChat\XPlugin\Plugins\WMPFRuntime\\" + version)
            os.system(r"rmdir /S /Q %APPDATA%\Tencent\WeChat\XPlugin\Plugins\WMPFRuntime\\" + version)
        except:
            pass
    subprocess.Popen(wechat)
    while True:
        dir_list = set(sorted(os.listdir(os.environ.get("APPDATA") + r"\Tencent\WeChat\XPlugin\Plugins\WMPFRuntime"),  key=lambda x: os.path.getmtime(os.path.join(os.environ.get("APPDATA") + r"\Tencent\WeChat\XPlugin\Plugins\WMPFRuntime", x)), reverse=True))
        versionSet = set()
        for i in range(5):
            try:
                response = requests.get('https://dldir1.qq.com/weixin/Windows/XPlugin/updateConfigWin.xml', proxies={'http': None, 'https': None}, verify = False)
            except:
                response = 0
            print(response)
            if response != 0:
                break
            time.sleep(1)
        content_dict = xmltodict.parse(response.text)
        plugins = content_dict['updateConfig']['Versions']['VersionInfo']
        for plugin in plugins:
            if plugin['@name'] == 'WMPFRuntime':
                versionSet.add(plugin['@version'])
        for version in [version for version in versionSet if version not in dir_list]:
            try:
                os.system('mkdir ' + os.path.join(persist + r"\WeChat\XPlugin\Plugins\WMPFRuntime", version + r"\extracted" ))
                os.system(r'powershell.exe "New-Item -Type Junction -Path $env:APPDATA\Tencent\WeChat\XPlugin\Plugins\WMPFRuntime\\' + version + r'\extracted -Target ' + persist + r'\WeChat\XPlugin\Plugins\WMPFRuntime\\' + version + r'\extracted"')
            except:
                pass
        for version in [version for version in dir_list if version not in versionSet]:
            try:
                os.system(r"rmdir /S /Q " + persist + r"\WeChat\XPlugin\Plugins\WMPFRuntime\\" + version)
                os.system(r"rmdir /S /Q %APPDATA%\Tencent\WeChat\XPlugin\Plugins\WMPFRuntime\\" + version)
            except:
                pass
        process_name='LogonUI.exe'
        callall='TASKLIST'
        outputall=subprocess.check_output(callall)
        outputstringall=str(outputall)
        if process_name in outputstringall:
            print("Locked.")
            if state == 0 and times >= 120:
                state = 1
                os.system('taskkill /F /IM "WeChat.exe"')
            elif times < 120:
                times += 1
        else:
            print("Unlocked.")
            if state == 1:
                state = 0
                times = 0
                subprocess.Popen(wechat)
            elif judgeprocess('WeChat.exe') == 1:
                exit()
        time.sleep(5)
