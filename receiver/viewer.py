import threading
from time import sleep
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QGridLayout, QLabel,QLineEdit,QGraphicsView,QGraphicsScene
from PyQt5.QtGui import QPainter,QPixmap,QImage
import PyQt5.QtCore as QtCore
import cv2
from ui_form import Ui_MainWindow
import receiver
from concurrent.futures import ThreadPoolExecutor
WIDTH = 1280
HEIGHT = 720

class Viewer(QMainWindow):
    def __init__(self,conf,receiver,imgprocess,logger):
        super(Viewer,self).__init__()
        self.buttonpushed = False
        self.logger = logger
        self.server_ = receiver
        self.process_ = imgprocess

        executor = ThreadPoolExecutor(max_workers=2)
        self.th1 = executor.submit(self.server_.processing)
        self.th2 = executor.submit(self.process_.start)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initUI()
        self.savedFrame = False
        self.endFlag = False

    def initUI(self):
        self.logger.info("initUI")

        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton.clicked.connect(self.startClient)
        self.ui.pushButton_2.clicked.connect(self.stopClient)
        self.ui.radioButton.setEnabled(False)

        self.scene = QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)  
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.mainloop)
        self.timer.start(33)


    def mainloop(self):
        self.logger.debug("mainloop")
        self.updateFrame()
        self.update()

    def paintEvent(self,event):
        self.logger.debug("paint EVENT")

        #TCP接続OK
        if(self.server_.getConnectStatus()):
            self.ui.radioButton.setEnabled(True)
            self.ui.radioButton.setChecked(True)

            #STARTボタン押下
            if(not self.buttonpushed):
                self.ui.pushButton.setEnabled(True)
                self.ui.pushButton_2.setEnabled(False)
        #TCP接続NG
        else:
            if(self.ui.radioButton.isChecked()):
                self.ui.radioButton.setChecked(False)
                self.ui.radioButton.setEnabled(False)

            self.ui.pushButton.setEnabled(False)
            self.ui.pushButton_2.setEnabled(False)
            self.buttonpushed = False

        self.logger.debug("paint EVENT END")


    def startClient(self):
        self.server_.sendStartMsg()
        self.ui.pushButton_2.setEnabled(True)
        self.ui.pushButton.setEnabled(False)
        self.buttonpushed = True
        self.logger.info('start')

    def stopClient(self):
        self.server_.sendEndMsg()
        self.logger.info('stop')
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton.setEnabled(False)
        self.buttonpushed = False

    def updateFrame(self):
        self.logger.debug("start updateframe")

        try:
            
            ret,tmpimg = self.process_.getFrame()
            currentwidht = self.ui.graphicsView.width()
            msg = "current windowsize -> width:" + str(currentwidht)
            currentheight = self.ui.graphicsView.height()
            self.logger.debug(msg)
            msg = "current windowsize -> height:" + str(currentheight)
            self.logger.debug(msg)

            img = cv2.resize(tmpimg, dsize=(int(currentwidht)-5,int(currentheight)-5))
            
            if(ret == True):
                self.logger.debug("update:new frame")
                self.savedFrame = True
                self.preFrame = img

            #遅延対策
            elif(ret == False and self.savedFrame ==True):
                self.logger.warn("update:delay frame")
                img = self.preFrame

            img = QImage(img, img.shape[1],
                            img.shape[0], img.shape[1] * 3,QImage.Format_RGB888)
            self.pixmap = QPixmap(img)
            self.scene.clear()
            self.scene.addPixmap(self.pixmap)

        except:
            self.logger.error("updateFrame err")

        self.logger.debug("end updateframe")
    
    #終了時処理
    def closeEvent(self,event):
        self.logger.info("closeEvent start")
        self.server_.stopProcessing()
        self.process_.stop()
        self.logger.info("closeEvent end")
        event.accept()


