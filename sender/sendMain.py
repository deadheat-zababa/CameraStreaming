import sys
import logging
import configparser
import threading
import queue
import sender
import frameprocess

logger = logging.getLogger('mylog')

def sendMain():

    conf = configparser.ConfigParser()
    conf.read('config/config.ini', 'UTF-8')

    frameq = queue.Queue()
    send = sender(conf,frameq)
    decode = frameprocess(conf,frameq)

    th1 = threading.Thread(target=send.process)
    decode.start()

    decode.join()
    send.stop()
    th1.join()

if __name__ == '__main__':
    sendMain()