import queue
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
        buf = self.image.get()

        if(buf.size == 0):
            return False,self.dummyimg
        else:
            return True,buf

    def getDummy(self):
        return self.dummyimg
    
    def getCode(self):
        buf = self.q.get()

        if(buf.size == 0):
            return False,buf
        else:
            return True,buf

    def start(self):

        while(self.stopFlag == False):
            ret,framecode = self.getCode()

            if(ret == True):
                #print("decode img")
                frame = cv2.imdecode(framecode,cv2.IMREAD_COLOR)
                self.image.put(frame)