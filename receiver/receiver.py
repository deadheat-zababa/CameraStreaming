# coding: utf-8
from logging import exception
from os import execv
import numpy as np
import time
import struct
import json
import threading
import sys
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
        self.headrecved = False
        self.count = 0
        self.datafirst = True
        
    def tcpReceiveProcess(self,recvdata):

        try:
            jdict = json.loads(recvdata)
            self.logger.info(jdict)
            identifier = list(jdict.keys())[0]

            msg = "received msg:" + identifier
            self.logger.debug(msg)

            if(identifier == "START_OK"):
                self.startFlag = True

            elif(identifier == "END_OK"):
                self.startFlag = False

            elif(identifier == "RTT_CAL"):
                seqno = jdict["RTT_CAL"]["seqno"]
                resdata = json.dumps({"RTT_RES":{"seqno":seqno}})
                self.tcpsock.send(resdata.encode())
            else:
                self.logger.error("tcpReceiveProcess : ERROR")
        except:
            self.logger.error("tcpReceiveProcess failed:recive data")
            raise Exception


    #receive a imagedata
    def udpReceiveProcess(self,recvdata):

        try:

            if(self.headrecved == False):
                jdict = json.loads(recvdata)
                self.logger.info(jdict)
                identifier = list(jdict.keys())[0]

                msg = "identifier : "+str(identifier)
                self.logger.info(msg)
                if(identifier == "IMAGE"):
                    self.size = int(jdict['IMAGE']['len'])
                    msg = "image size : "+str(self.size)
                    self.logger.info(msg)
                    self.headrecved = True
                    self.count = int(self.size/1024)
                    msg = "recv count:" + str(self.count)
                    self.logger.info(msg)

            else:
                msg = "recvdata size:" + str(len(recvdata))
                self.logger.info(msg)

                if self.count != 0:
                    
                    msg = "count : "+ str(self.count)
                    self.logger.info(msg)

                    msg = "recv imagedata : "+ str(recvdata)
                    self.logger.info(msg)

                    if self.datafirst == True:
                        self.img = np.frombuffer(recvdata,dtype=np.uint8)
                        self.datafirst = False
                    else:
                        self.img = np.append(self.img,np.frombuffer(recvdata,dtype=np.uint8))
                else:
                    msg = "count : 0" 
                    self.logger.info(msg)
                    msg = "recv imagedata : "+ str(recvdata)
                    self.logger.info(msg)
                    self.img = np.append(self.img,np.frombuffer(recvdata,dtype=np.uint8))

                self.size = self.size - 1024
                self.count = self.count -1

                if(self.count == -1):
                    self.img = self.img.reshape(self.size,1)
                    self.frame.put(self.img)
                    self.logger.info("input q")
                    self.headrecved = False
                    self.count = 0
                    self.datafirst = True
        
        except:
            self.logger.error("udpReceiveProcess error")
            msg = "recedata:" + str(recvdata)
            self.logger.info(msg)
            self.headrecved == False
            self.datafirst = True
            self.count = 0
            self.size = 0

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

        th1 = threading.Thread(target=self.tcpsock.receive)
        th2 = threading.Thread(target=self.udpsock.receive)

        th1.start()
        th2.start()

        while(not self.stopFlag):
            time.sleep(1/120)

        self.tcpsock.stop()
        self.udpsock.stop()

        th1.join()
        th2.join()

        self.logger.info("receiver END")