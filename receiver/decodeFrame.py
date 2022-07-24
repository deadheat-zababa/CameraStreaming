import queue
import time
import cv2
import torch

class decodeFrame():
    def __init__(self,conf,q,dummyPaht,logger):
        self.codeq = q
        self.image = queue.Queue()
        self.stopFlag = False
        self.dummyimg = cv2.imread(dummyPaht)
        self.logger = logger
        
    def stop(self):
        self.stopFlag = True

    def getFrame(self):
        self.logger.debug("getFrame start")
        size = self.image.qsize()

        if(size == 0):
            self.logger.debug("buf = 0")
            
            return False,self.dummyimg
        else:
            self.logger.debug("buf != 0")
            return True,self.image.get()

    def getDummy(self):
        return self.dummyimg
    
    def getCode(self):

        self.logger.debug("getCode start")
        size = self.codeq.qsize()

        if(size == 0):
            self.logger.debug("buf = 0")
            return False,self.dummyimg
        else:
            self.logger.debug("buf != 0")
            return True,self.codeq.get()

    def start(self):
        self.logger.info("decode frame start")
        
        while(self.stopFlag == False):
            ret,framecode = self.getCode()

            if(ret == True):
                self.logger.info("decode img")
                frame = cv2.imdecode(framecode,cv2.IMREAD_COLOR)
                self.image.put(frame)
            else:
                time.sleep(1/120)

        self.logger.info("decode frame end")