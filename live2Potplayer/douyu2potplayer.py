import configparser
import os
import sys

from lib.douyu import DouYu

if __name__ == "__main__":
    ID = sys.argv[1]
    config = configparser.ConfigParser()
    config.read(os.path.split(os.path.realpath(__file__))[0] + '\\config.ini')
    persist = config.get('baseconf', 'persist')
    try:
        s = DouYu(ID)
    except Exception as ex:
        with open('test.txt', 'w') as file:
            file.write("出现如下异常%s"%ex)
    os.system(persist + '\\apps\\potplayer\\current\\PotPlayerMini64.exe "' + s.get_real_url() + '"')
