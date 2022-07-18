import threading
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel,QLineEdit,QPainter
from Pyside import QtCore
import receiver

class Viewer(QWidget):

    def __init__(self,receiver,imgprocess):
        super().__init__()
        self.initUI()
        self.server_ = receiver
        self.process_ = imgprocess
        self.th1 = threading.Thread(target=self.server_.processing)
        self.th2 = threading.Thread(target=self.process_.start)

    def initUI(self):
        self.setGetmetry(0,0,1920,1080)
        self.setWindowTitle('Camera Viewer')

        self.ipaddrlabel = QLabel('status : ')
        self.ledlamp = QPainter(self)
        self.ledlamp.setBruch(QtCore.Qt.red)
        self.ledlamp.drawRect(50,50,100,100)

        self.startButton = QPushButton('START')
        self.stopButton = QPushButton('STOP')
        self.inputip = QLineEdit(self)
        self.inputvport = QLineEdit(self)

        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.startButton.clicked.connect(self.startClient)
        self.stopButton.clicked.connect(self.stopClient)

        self.ledlamp.connect(self.updateStatus)


        self.grid = QGridLayout()

        #                                    (y,x,y,x)
        self.grid.addWidget(self.setButton,   3, 0, 3, 5)
        self.grid.addWidget(self.stopButton,  5, 2, 6, 3)

        self.setLayout(self.grid)
        self.show()

    def startClient(self):
        self.server_.sendStartMsg()
        self.stopButton.setEnabled(True)
        self.startButton.setEnabled(False)
        
        print('start')

    def stopClient(self):
        self.server_.sendEndMsg()
        print('stop')
        self.stopButton.setEnabled(False)
        self.startButton.setEnabled(True)
        
    def updateFrame(self):
        self.process_.getFrame()

    def updateStatus(self):
        if(self.server_.getConnectStatus()):
            self.ledlamp.setBruch(QtCore.Qt.green)
            self.startButton.setEnabled(True)
        else:
            self.ledlamp.setBruch(QtCore.Qt.red)
            self.startButton.setEnabled(False)
        
    #終了時処理
    def closeEvent(self,event):
        self.server_.stop()
        self.process_.stop()
        self.th1.join()
        self.th2 .join()
        event.accept()


