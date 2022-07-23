# coding: utf-8
from xml.dom.minidom import Identified
import logging
import queue
import time
import struct
import json
import pprint
from tcpnet import tcpnet
from udpnet import udpnet
import threading


class receiver:
    def __init__(self,conf,q):
        self.connnectStatus = False
        self.startFlag = False
        self.tcpsock = tcpnet(conf['info']['srcipaddr'],int(conf['info']['tcpport']))
        self.udpsock = udpnet(conf['info']['srcipaddr'],conf['info']['dstipaddr'],int(conf['info']['udpsendport']),int(conf['info']['udprecvport']))
        self.frame = q
        self.len = 0
        self.stopFlag = False
        
    def tcpReceiveProcess(self,recvdata):
        jdict = json.loads(recvdata)
        
        identifier = jdict[0]

        if(identifier == "START_OK"):
            self.startFlag = True

        elif(identifier == "END_OK"):
            self.startFlag = False

        elif(identifier == "RTT_CAL"):
            seqno = jdict["RTT_CAL"]["seqno"]
            resdata = json.dumps({"RTT_RES":{"seqno":seqno}})
            self.tcpsock.send(struct.pack('>L',resdata))
        else:
            print("ERROR")

    #receive a imagedata
    def udpReceiveProcess(self,recvdata):

        #{"IMAGE":{"seqno":n,"len"xxxxx}}
        jdict = json.loads(recvdata)

        #pprint.pprint(jdict,width=40)

        identifier = jdict[0]

        if(identifier == "IMAGE"):
            size = jdict['IMAGE']['len']

            
        if size > 1024:
            count = int(size/1024)

            for i in range(count):
          
                tmp = self.udpsock.recv(1024)
          
                if i == 0:
                    img = np.frombuffer(tmp,dtype=np.uint8)
                else:
                    img = np.append(img,np.frombuffer(tmp,dtype=np.uint8))

            tmp = self.udpsock.recv(int(size%1024))
            img = np.append(img,np.frombuffer(tmp,dtype=np.uint8))

        else:
            tmp = self.udpsock.recv(size)
            img = np.frombuffer(tmp,dtype=np.uint8)

        img = img.reshape(size,1)
        #print("input q")
        self.frame.put(img)

    def getConnectStatus(self):
        return self.tcpsock.getConnectStatus()

    def sendStartMsg(self):
        startdata = json.dumps({"START":{}})
        #self.tcpsock.send(struct.pack('>L'),startdata.encode())
        #self.tcpsock.send(struct.pack('>L'))
        self.tcpsock.send(startdata.encode())

    def sendEndMsg(self):
        enddata = json.dumps({"END":{}})
        self.tcpsock.send(struct.pack('>L'),enddata.encode())
        self.startFlag = True

    def setFrame(self):
        return self.frame

    def stopProcessing(self):
        self.stopFlag = True

    def processing(self):
        #logging.info("receiver START")
        print("PROCESSING START")
        self.tcpsock.setReceiveProcess(self.tcpReceiveProcess)
        self.udpsock.setReceiveProcess(self.udpReceiveProcess)

        th1 = threading.Thread(target=self.tcpsock.receive)
        th2 = threading.Thread(target=self.udpsock.receive)

        th1.start()
        th2.start()

        while(not self.stopFlag):
            time.sleep(1/120)

        self.tcpsock.stop()
        th1.join()
        self.udpsock.stop()
        th2.join()

        #logging.info("receiver END")