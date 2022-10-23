import sys
import logging
import configparser
import queue
from PyQt5.QtWidgets import QApplication
from receiver import receiver
from decodeFrame import decodeFrame
from viewer import Viewer
sys.path.append("../common")
from myLog import myLog

def receiveMain():

    logger = myLog("receiver.log")
    logger.info("--receiver START--")

    conf = configparser.ConfigParser()
    conf.read('config/setting.ini', 'UTF-8')

    logger.setLogLevel(int(conf['info']['loglevel']))

    app = QApplication(sys.argv)

    framecodeq = queue.Queue()
    receive = receiver(conf,framecodeq,logger)
    decode = decodeFrame(conf,framecodeq,"img/dummy.jpg",logger)
    view = Viewer(conf,receive,decode,logger)

    view.show()

    ret = app.exec_()
    logger.info("--receiver END--")
    sys.exit(ret)
    

if __name__ == '__main__':
    receiveMain()