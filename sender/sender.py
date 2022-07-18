# coding: utf-8
from xml.dom.minidom import Identified
import logging
import queue
import time
import struct
import json
import pprint
import tcpnet
import udpnet
import threading


class sender():
    def __init__(self,conf,fprocess):
        self.connnectStatus = False
        self.startFlag = False
        self.tcpsock = tcpnet(conf['info']['dstipaddr'],conf['info']['tcpport'])
        self.udpsock = udpnet(conf['info']['srcipaddr'],conf['info']['dstipaddr'],conf['info']['udpsendport'],conf['info']['udprecvport'])
        self.frame = queue.Queue()
        self.len = 0
        self.stopFlag = False
        self.framep = fprocess
        self.sendtime = int(time.time() * 1000)
        self.recvtime = int(time.time() * 1000)
        self.quality = int(conf['info']['quality'])
        self.threshold = int(conf['info']['rtt_threshold'])
        self.interval_ = int(conf['info']['rtt_sendinterval'])

        
    def tcpReceiveProcess(self,recvdata):
        jdict = json.loads(recvdata)
        
        identifier = jdict[0]

        if(identifier == "START"):
            self.startFlag = True

        elif(identifier == "END"):
            self.startFlag = False

        elif(identifier == "RTT_CAL"):
            self.recvtime = int(time.time() * 1000)
            self.calcTAT()
        else:
            print("ERROR")

    def getConnectStatus(self):
        return self.connnectStatus

    def setFrame(self):
        return self.frame

    def stopProcessing(self):
        self.stopFlag = True


    def calcTAT(self):
        
        if((self.recvtime - self.sendtime)>self.threshold):
            self.quality = self.quality -5
            if(self.quality < 10):
                self.quality = 10
        else:
            self.quality = self.quality +5
            if(self.quality > 90):
                self.quality = 90

        self.fprocess.update(self.quality)

    def rttsend(self):
        seqno = 0
        while(not self.stopFlag):
            rttdata = json.dumps({"RTT_CAL":{"seqno":seqno}})
            self.tcpsock.send(struct.pack('>L',rttdata))
            seqno = seqno +1
            if(seqno > 999):
                seqno = 0
            self.sendtime = int(time.time() * 1000)

            time.sleep(self.interval_)

    def processing(self):
        logging.info("sender START")
        self.tcpsock.setReceiveProcess(self.tcpReceiveProcess)
        th1 = threading.Thread(target=self.tcpsock.receive)
        seqmo = 0

        while(not self.stopFlag):
            encimg = self.fprocess.getCode()

            if(self.startFlag == False):
                time.sleep(1/30)
                continue

            imagedata = {"IMAGE":{"seqno":seqno,"len":encimg.size}}
            self.udpsock.send(struct.pack('>L',imagedata))

            if encimg.size > 1024:
                encimg.ravel
                length = int(encimg.size/1024)
                #print(length)
                cnt = 0
                for i in range(length):
                    self.udpsock.send(encimg[cnt:i*1024+1024].tobytes())
                    cnt += 1024
                    #tmp_img = encimg[cnt:i*1024+1024].tobytes()
                    #print(type(tmp_img))

                self.udpsock.send(encimg[cnt:(cnt+int(encimg.size%1024))].tobytes())
                #print(encimg[cnt:(cnt+int(encimg.size%1024))])
                #print((i+int(encimg.size%1024)))
            else:
                self.udpsock.send(encimg.tobytes())

            seqno = seqno+1


        self.tcpsock.stop()
        th1.join()

        logging.info("receiver END")