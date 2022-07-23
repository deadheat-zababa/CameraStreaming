import sys
import logging
import configparser
import queue
from PyQt5.QtWidgets import QApplication
from receiver import receiver
from decodeFrame import decodeFrame
from viewer import Viewer



logger = logging.getLogger('mylog')

def receiveMain():

    conf = configparser.ConfigParser()
    conf.read('config/setting.ini', 'UTF-8')

    app = QApplication(sys.argv)

    framecodeq = queue.Queue()
    receive = receiver(conf,framecodeq)
    decode = decodeFrame(conf,framecodeq,"img/dummy.jpg")
    view = Viewer(conf,receive,decode)

    view.show()

    ret = app.exec_()
    sys.exit(ret)

if __name__ == '__main__':
    receiveMain()