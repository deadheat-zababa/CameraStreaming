import queue
import time
import cv2

class decodeFrame():
    def __init__(self,conf,q,dummyPaht):
        self.q = q
        self.image = queue.Queue()
        self.stopFlag = False
        self.dummyimg = cv2.imread(dummyPaht)

    def stop(self):
        self.stopFlag = True

    def getFrame(self):
        print("getFrame start")
        size = self.image.qsize()

        if(size == 0):
            print("buf = 0")
            return False,self.dummyimg
        else:
            print("buf != 0")
            return True,self.image.get()

    def getDummy(self):
        return self.dummyimg
    
    def getCode(self):

        print("getCode start")
        size = self.image.qsize()

        if(size == 0):
            print("buf = 0")
            return False,self.dummyimg
        else:
            print("buf != 0")
            return True,self.q.get()

    def start(self):

        while(self.stopFlag == False):
            ret,framecode = self.getCode()

            if(ret == True):
                #print("decode img")
                frame = cv2.imdecode(framecode,cv2.IMREAD_COLOR)
                self.image.put(frame)
            else:
                time.sleep(1/120)