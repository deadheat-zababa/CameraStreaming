import sys
import logging
import configparser
import queue
import viewer
from PyQt5.QtWidgets import QApplication
from receiver.decodeFrame import decodeFrame
from receiver.receiver import receiver

logger = logging.getLogger('mylog')

def receiveMain():

    conf = configparser.ConfigParser()
    conf.read('config/config.ini', 'UTF-8')

    app = QApplication(sys.argv)

    framecodeq = queue.Queue()
    receive = receiver(conf,framecodeq)
    decode = decodeFrame(conf,framecodeq,"img/dummy.jpg")
    view = viewer(conf,receive,decode)

    ret = app.exec_()
    sys.exit(ret)

if __name__ == '__main__':
    receiveMain()