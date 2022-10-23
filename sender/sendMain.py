from base64 import encode
from cmath import log
import sys

import configparser
import threading
import queue
from sender import sender
from frameprocess import frameprocess
import signal
import time
sys.path.append("../common")
from myLog import myLog


global_stopFlag = False

def handler(signal, frame):
    print("ctrl-c")
    global global_stopFlag
    global_stopFlag = True

def sendMain():
    global global_stopFlag
    signal.signal(signal.SIGINT, handler)

    logger = myLog("sender.log")
    logger.info("sender START")

    conf = configparser.ConfigParser()
    conf.read('config/setting.ini', 'UTF-8')

    logger.setLogLevel(int(conf['info']['loglevel']))

    frameq = queue.Queue()
    encode = frameprocess(conf,frameq,logger)
    send = sender(conf,encode,logger)
    
    th1 = threading.Thread(target=send.processing)
    th1.start()
    encode.start()

    while(global_stopFlag == False):
        time.sleep(1/120)

    send.stopProcessing()
    th1.join()

    encode.stop()
    encode.join()

    logger.info("sender END")
    

if __name__ == '__main__':
    sendMain()