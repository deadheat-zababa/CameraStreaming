import threading
import cv2
import pyvirtualcam
import logging
import time
from myLog import myLog


class frameprocess(threading.Thread):

    def __init__(self,conf,q,logger):
        threading.Thread.__init__(self)
        self.q = q
        self.camid_ = int(conf['info']['camid'])
        self.quality_ = int(conf['info']['quality'])
        self.stop_event =threading.Event()
        self.setDaemon(True)
        self.logger = logger
        self.stopflag = False
        self.framerate= float(conf['info']['framerate'])
        self.qMax = 3

    def stop(self):
        self.stopflag = True
        self.stop_event.set()
    
    def updateQuqlity(self,quality):
        self.quality_ =  quality

    def setCode(self,framecode):
        if(self.q.qsize() == self.qMax):
            tmp = self.q.get()
        self.q.put(framecode)

    def getCode(self):
        if(self.q.qsize() == 0):
            return False,'0b000000'
        else:    
            return True,self.q.get()

    def run(self):
        
        self.logger.info("frameprocess Thread Start")
        
        capture = cv2.VideoCapture(self.camid_)

        while(not self.stopflag):
            try:

                self.logger.debug("while loop")
                ret,frame = capture.read()

                #get frame data
                self.logger.debug("img encode")
                frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
                ret, encimg = cv2.imencode(".jpg",frame,[int(cv2.IMWRITE_JPEG_QUALITY),self.quality_])
                if False == ret:
                    self.logger.error("Encode error")
                    continue

                else:
                    msg = "Encode OK:"+str(encimg.shape)
                    self.logger.debug(msg)
                    self.setCode(encimg)
                    #print(type(encimg))
                    #print(encimg.size)
                msg = "Sleep:" + str(1/self.framerate)
                self.logger.debug(msg)
                time.sleep(1/self.framerate)
            except KeyboardInterrupt:
                self.logger.info("frameprocess Thread Ctrl-C")
                break

        capture.release()
        cv2.destroyAllWindows()
        self.logger.info("frameprocess Thread End")