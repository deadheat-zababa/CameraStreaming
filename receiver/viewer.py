import threading
from time import sleep
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel,QLineEdit,QGraphicsView,QGraphicsScene
from PyQt5.QtGui import QPainter,QPixmap,QImage
import PyQt5.QtCore as QtCore
import receiver

WIDTH = 1280
HEIGHT = 720

class Viewer(QWidget):
    
    def __init__(self,conf,receiver,imgprocess):
        super().__init__()
        self.server_ = receiver
        self.process_ = imgprocess
        self.th1 = threading.Thread(target=self.server_.processing)
        self.th2 = threading.Thread(target=self.process_.start)
        self.th1.start()
        self.th2.start()
        self.initUI()
        print("end init")

    def initUI(self):
        print("initUI")
        self.resize(1500,800)
        self.setWindowTitle('Camera Viewer')

        self.statuslabel = QLabel(':  status')
        #self.ledlamp = QPainter(self)
        #self.ledlamp.begin(self)
        #self.ledlamp.setBrush(QtCore.Qt.red)
        

        self.startButton = QPushButton('START')
        self.stopButton = QPushButton('STOP')

        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.startButton.clicked.connect(self.startClient)
        self.stopButton.clicked.connect(self.stopClient)

        self.grid = QGridLayout()

        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)  
        self.grid.addWidget(self.view,0,0,3,1)
        #self.grid.addWidget(self.ledlamp,0,1,1,1)
        self.grid.addWidget(self.statuslabel, 0,2,1,1) 
        self.grid.addWidget(self.startButton, 1,1,1,2)
        self.grid.addWidget(self.stopButton,  2,1,1,2)

        self.setLayout(self.grid)

        #self.ledlamp = QPainter(self)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.mainloop)
        self.timer.start(300)


    def mainloop(self):
        print("mainloop")
        self.updateFrame()
        self.update()

    def paintEvent(self,event):
        print("paint EVENT")
        ledlamp = QPainter(self)

        #ledlamp.begin(self)

        ledlamp.setPen(QtCore.Qt.black)
        if(self.server_.getConnectStatus()):
            ledlamp.setBrush(QtCore.Qt.green)
            self.startButton.setEnabled(True)
        else:
            ledlamp.setBrush(QtCore.Qt.red)
            self.startButton.setEnabled(False)

        ledlamp.drawEllipse(QtCore.QPointF(1430,370), 10, 10)

        #ledlamp.end()

        print("paint EVENT END")


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
        print("start updateframe")
        try:
            ret,img = self.process_.getFrame()
            img = QImage(img, img.shape[1],
                            img.shape[0], img.shape[1] * 3,QImage.Format_RGB888)
            self.pixmap = QPixmap(img)
            self.scene.clear()
            self.scene.addPixmap(self.pixmap)
        except:
            print("updateFrame err")

        print("end updateframe")
    
    #終了時処理
    def closeEvent(self,event):
        print("closeEvent")
        self.server_.stopProcessing()
        self.process_.stop()
        self.th1.join()
        self.th2 .join()
        event.accept()


