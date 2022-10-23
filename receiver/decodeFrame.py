import queue
import time
import cv2
import os

class decodeFrame():
    def __init__(self,conf,q,dummyPaht,logger):
        self.codeq = q
        self.image = queue.Queue()
        self.stopFlag = False
        self.dummyimg = cv2.imread(dummyPaht)
        self.logger = logger
        self.outputflag = int(conf['info']['outputflag'])
        
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
            self.logger.debug("buf = "+ str(size))
            return True,self.codeq.get()

    def decodeprocessing(self,framecode):

        print(framecode)
        print("decode bofore")
        try:
            frame = cv2.imdecode(framecode,cv2.IMREAD_COLOR)
        except:
            print("d error")
        print("decode")
        print(frame)
        if(type(frame) != None):
            self.image.put(frame)
                 
    def start(self):
        self.logger.info("decode frame start")
        self.logger.info("decodeprocessing start")
        
        while(self.stopFlag == False):
            ret,framecode = self.getCode()

            if(ret == True):
                self.logger.info("decode img")
                time_sta = time.time()

                self.logger.info("process start")

                frame = cv2.imdecode(framecode,cv2.IMREAD_COLOR)

                time_end = time.time()
                diff_time = time_end- time_sta
                self.logger.info("decode time : "+str(diff_time))

                if(type(frame) == None):
                    self.logger.error("decode failed: empty frame")
                else:
                    self.image.put(frame)
                  
                if(1 == self.outputflag):
                    if(not os.path.exists("./datalog")):
                        os.mkdir("./datalog")
                    self.logger.debug("self.outputflag -> True")
                    output = "datalog/" + str(int(time.time() * 1000)) + ".jpg"
                    ff = open(output, 'wb') 
                    ff.write(framecode.tobytes())
                    ff.close()
            
            time.sleep(1/120)

        

        self.logger.info("decode frame end")