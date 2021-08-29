# coding: utf-8
import cv2
import numpy as np
import logging
import threading
import queue
import time
import socket
import struct
import sys
import json
import pprint
import pyvirtualcam

global_ipaddr = "127.0.0.1"
global_cport = 0
global_vport = 0
global_stopFlag = False


class viewThread(threading.Thread):
    def __init__(self,timestamp,q):
        threading.Thread.__init__(self)
        self.timestamp = timestamp
        self.q = q
        self.stop_event =threading.Event()
        self.setDaemon(True)

    def stop(self):
        self.stop_event.set()

    def getFrame(self):
        buf = self.q.get()

        #if(buf.size == 0):
            #img = np.zeros(sys.getsizeof(buf))
            #return False,buf
        #else:
        return True,buf


    def run(self):
        print("run run run")
        print(self.timestamp-int(time.time()))
        #time.sleep(self.timestamp-int(time.time()))

        cam = pyvirtualcam.Camera(width=1280,height=720,fps=30)

        while(global_stopFlag == False):
            print("show frame")
            ret,frame = self.getFrame()
            print(frame)

            if(ret == True):
                print("decode img")
                img = cv2.imdecode(frame,cv2.IMREAD_COLOR)
                print(img.shape)
                print(type(img))
                if(img.size == 0):
                    print("SIZE NONE")
                else:
                    print("DECODE SUCCESS")
                    cam.send(img)
                    cam.sleep_util_next_frame()
                #cv2.imshow('TEST',img)
                #cv2.imwrite('test1.jpg',img)
                
                #cv2.waitKey(1)
                #time.sleep(1/30)
            else:
                print("eeror")
        cam.close()
        #cv2.destroyAllWindows()


def stop():
    global_stopFlag = True

def clientMain(ipaddr,videoPort):#,controlPort):
    #loggging.info("START")
    
    waitFlg = 1

    #制御信号用スレッド起動
    #control = controlThread()

    #同期完了まで待つ
    #while waitFlg:
    #    sleep(1/30)

    q = queue.Queue()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #s.connect((ipaddr, int(videoPort)))
    #s.connect((socket.gethostname(), int(videoPort)))
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((socket.gethostname(),int(videoPort)))
    s.listen(5)
    logging.info("socket Thread Start")

    s,address = s.accept()
    s.send(struct.pack('>L',int(time.time())+1))
    #timestamp = struct.unpack('>L',s.recv(1024))
    #print("timestmp:%d",timestamp[0])
    t1 = viewThread(time.time(),q)
    t1.start()

    while(global_stopFlag == False):
        #size = struct.unpack('>L',s.recv(1024))
        jdict = json.loads(s.recv(1024))
        pprint.pprint(jdict,width=40)
        size = jdict['size']
        print(size)

        if(jdict['id']=='end'):
            break

        if size > 1024:
            count = int(size/1024)

            for i in range(count):
          
                tmp = s.recv(1024)
          
                if i == 0:
                    img = np.frombuffer(tmp,dtype=np.uint8)
                else:
                    img = np.append(img,np.frombuffer(tmp,dtype=np.uint8))

            tmp = s.recv(int(size%1024))
            img = np.append(img,np.frombuffer(tmp,dtype=np.uint8))

        else:
            tmp = s.recv(size)
            img = np.frombuffer(tmp,dtype=np.uint8)

        img = img.reshape(size,1)
        print("input q")
        q.put(img)

    s.close()
    t1.stop()
    #control.stop()


if __name__ == '__main__':
    clientMain("127.0.0.1",12345)
