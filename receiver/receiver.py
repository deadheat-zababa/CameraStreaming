# coding: utf-8
from logging import exception
from os import execv
import numpy as np
import time
import struct
import json
import threading
import sys
import collections

from concurrent.futures import ThreadPoolExecutor
sys.path.append("../common")
from tcpnet import tcpnet
from udpnet import udpnet

class receiver:
    def __init__(self,conf,q,logger):
        self.connnectStatus = False
        self.startFlag = False
        self.tcpsock = tcpnet(conf['info']['srcipaddr'],int(conf['info']['tcpport']),1,logger)
        self.udpsock = udpnet(conf['info']['srcipaddr'],conf['info']['dstipaddr'],int(conf['info']['udpsendport']),int(conf['info']['udprecvport']),logger)
        self.frame = q
        self.size = 0
        self.stopFlag = False
        self.logger = logger
        self.count = 0
        self.img = ""
        self.failedcnt = 0
        self.recvbuf = collections.deque([],10)
        
    def tcpReceiveProcess(self,recvdata):

        try:
            jdict = json.loads(recvdata)
            self.logger.debug(str(jdict))
            identifier = list(jdict.keys())[0]

            msg = "received msg:" + identifier
            self.logger.debug(msg)

            if(identifier == "START_OK"):
                self.logger.debug("recv START : startFlag=> True")
                self.startFlag = True

            elif(identifier == "END_OK"):
                self.logger.debug("recv END : startFlag=> False")
                self.startFlag = False

            elif(identifier == "RTT_CAL"):
                seqno = jdict["RTT_CAL"]["seqno"]
                resdata = json.dumps({"RTT_RES":{"seqno":seqno,"failedcnt":self.failedcnt}})
                self.tcpsock.send(resdata.encode())
            else:
                self.logger.error("tcpReceiveProcess : ERROR")
        except:
            self.logger.error("tcpReceiveProcess failed:recive data")
            raise Exception


    def is_json(self,recvdata):
        try:
            jdict = json.loads(recvdata)
            self.logger.debug("recv json message")
            return True
        except:
            self.logger.debug("recv binary message")
            return False

    #receive a imagedata
    def udpReceiveProcess(self,recvdata):
        if(len(recvdata)>0):
            self.recvbuf.append(recvdata)

    def udpRecvBufProcess(self):
        while(not self.stopFlag):
            bufsize = len(self.recvbuf)
            if(bufsize>0):
                recvdata = self.recvbuf.popleft()
                self.logger.debug("buffer size:"+str(bufsize))
            else:
                self.logger.debug("buffer 0")
                time.sleep(1/1000)
                continue
            try:
                ret = self.is_json(recvdata)           
                if(True == ret):
                    jdict = json.loads(recvdata)
                    self.logger.debug(str(jdict))
                    identifier = list(jdict.keys())[0]

                    msg = "identifier : "+str(identifier)
                    self.logger.debug(msg)
                    if(identifier == "IMAGE"):
                        if(self.size != 0):
                            self.failedcnt = self.failedcnt + 1
                            self.logger.error("image data lost : " + str(self.failedcnt))
                        
                        self.size = int(jdict['IMAGE']['len'])
                        msg = "image size : "+ str(self.size)
                        self.logger.debug(msg)
                        self.count = int(self.size/4096)#1024)
                        msg = "recv count:" + str(self.count)
                        self.logger.debug(msg)

                else:
                    msg = "recvdata size:" + str(len(recvdata))
                    self.logger.debug(msg)

                    if self.count != 0:
                        
                        msg = "count : "+ str(self.count)
                        self.logger.debug(msg)

                        msg = "recv imagedata : "+ str(recvdata)
                        self.logger.debug(msg)
                        if(len(self.img) == 0):
                            self.img = np.frombuffer(recvdata,dtype=np.uint8)
                        else:
                            self.img = np.append(self.img,np.frombuffer(recvdata,dtype=np.uint8))

                    else:
                        msg = "count : 0" 
                        self.logger.debug(msg)
                        msg = "recv imagedata : "+ str(recvdata)
                        self.logger.debug(msg)
                        self.img = np.append(self.img,np.frombuffer(recvdata,dtype=np.uint8))

                    self.count = self.count -1

                    if(self.count == -1):
                        self.img = self.img.reshape(self.size,1)
                        self.frame.put(self.img)

                        self.logger.info("input q")
                        self.count = 0
                        self.img = ""
            
            except:
                self.logger.error("udpReceiveProcess error")
                msg = "recedata:" + str(recvdata)
                self.logger.error(msg)
                self.count = 0
                self.size = 0
                self.img = ""

    def getConnectStatus(self):
        return self.tcpsock.getConnectStatus()

    def sendStartMsg(self):
        startdata = json.dumps({"START":{}})
        self.tcpsock.send(startdata.encode())

    def sendEndMsg(self):
        enddata = json.dumps({"END":{}})
        self.tcpsock.send(enddata.encode())
        self.startFlag = False

    def setFrame(self):
        return self.frame

    def stopProcessing(self):
        self.stopFlag = True

    def processing(self):
        self.logger.info("PROCESSING START")
        self.tcpsock.setReceiveProcess(self.tcpReceiveProcess)
        self.udpsock.setReceiveProcess(self.udpReceiveProcess)

        th3 = threading.Thread(target=self.udpRecvBufProcess)

        executor = ThreadPoolExecutor(max_workers=4)
        self.th1 = executor.submit(self.tcpsock.receive)
        self.th2 = executor.submit(self.udpsock.receive)
        
        th3.start()
        
        th3.join()

        self.tcpsock.stop()
        self.udpsock.stop()        

        self.logger.info("receiver END")