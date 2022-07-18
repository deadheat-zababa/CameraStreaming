import threading
import cv2
import logging
import time

logger = getLogger("log").getChild("")

class frameprocess(threading.Thread):

    def __init__(self,conf,q):
        threading.Thread.__init__(self)
        self.q = q
        self.camid_ = int(conf['info']['camid'])
        self.quality_ = int(conf['info']['quality'])
        self.stop_event =threading.Event()
        self.setDaemon(True)

    def stop(self):
        self.stop_event.set()
    
    def updateQuqlity(self,quality):
        self.quality_ =  quality

    def setCode(self,framecode):
        self.q.put(framecode)

    def getCode(self):
        return self.q.get()

    def run(self):
        
        logging.info("socket Thread Start")
        
        capture = cv2.VideoCapture(self.camid_)

        while(True):
            print("while loop")
            ret,frame = capture.read()
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("end")
                break

            else:
                logging.debug("frame:%d,%s",frame.size,frame.shape)

            #get frame data
            print("img encode")
            ret, encimg = cv2.imencode(".jpg",frame,[int(cv2.IMWRITE_JPEG_QUALITY),self.quality_])
            if False == ret:
                logging.error("Encode error")
                continue

            else:
                logging.info("Encode OK:%s",encimg.shape)
                self.setCode(encimg)
                #print(type(encimg))
                #print(encimg.size)

            logging.debug("Sleep:%f",1/capture.get(3))
            time.sleep(1/capture.get(3))
        
        capture.release()
        cv2.destroyAllWindows()