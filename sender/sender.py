# coding: utf-8
import queue
import time
import struct
import json
import sys
import os
import numpy as np
sys.path.append("../common")
from tcpnet import tcpnet
from udpnet import udpnet
import threading

class sender():
    def __init__(self,conf,fprocess,logger):
        self.startFlag = False
        self.tcpsock = tcpnet(conf['info']['dstipaddr'],int(conf['info']['tcpport']),0,logger)
        self.udpsock = udpnet(conf['info']['srcipaddr'],conf['info']['dstipaddr'],int(conf['info']['udpsendport']),int(conf['info']['udprecvport']),logger)
        self.frame = queue.Queue()
        self.len = 0
        self.stopFlag = False
        self.framep = fprocess
        self.sendtime = int(time.time() * 1000)
        self.recvtime = int(time.time() * 1000)
        self.quality = int(conf['info']['quality'])
        self.threshold = int(conf['info']['rtt_threshold'])
        self.interval_ = int(conf['info']['rtt_sendinterval'])/1000
        self.logger = logger
        self.rttes = np.repeat([self.threshold], 5)
        self.outputflag = int(conf['info']['outputflag'])

    def tcpReceiveProcess(self,recvdata):
        try:
            jdict = json.loads(recvdata)
            self.logger.info(str(jdict))
            identifier = list(jdict.keys())[0]

            msg = "received msg:" + identifier
            self.logger.info(msg)

            if(identifier == "START"):
                self.startFlag = True
                startdata = json.dumps({"START_OK":{}})
                self.tcpsock.send(startdata.encode())

            elif(identifier == "END"):
                self.startFlag = False
                startdata = json.dumps({"END_OK":{}})
                self.tcpsock.send(startdata.encode())

            elif(identifier == "RTT_RES"):
                self.recvtime = int(time.time() * 1000)
                self.calcTAT()
            else:
                self.logger.error("ERROR")
        except:
            self.logger.error("tcpReceiveProcess failed:recive data")
            self.startFlag = False
            raise Exception

    def getConnectStatus(self):
        return self.tcpsock.getConnectStatus()

    def setFrame(self):
        return self.frame

    def stopProcessing(self):
        self.stopFlag = True


    def calcTAT(self):
        np.roll(self.rttes, 1)
        self.rttes[-1] = self.recvtime - self.sendtime
        rtt = np.average(self.rttes)
        if(rtt > self.threshold):
            self.quality = self.quality -5
            if(self.quality < 10):
                self.quality = 10
        else:
            self.quality = self.quality +5
            if(self.quality > 90):
                self.quality = 90
        self.logger.info("rtt : " + str(rtt) +", quality : " + str(self.quality))
        self.framep.updateQuqlity(self.quality)
        self.threshold = rtt

    def rttsend(self):
        seqno = 0
        while(not self.stopFlag):
            if(True == self.startFlag and True == self.getConnectStatus()):
                rttdata = json.dumps({"RTT_CAL":{"seqno":seqno}})
                msg = "[RTT]senddata:" + str(rttdata)
                self.logger.info(msg)
                self.tcpsock.send(rttdata.encode())
                seqno = seqno +1
                if(seqno > 999):
                    seqno = 0
                self.sendtime = int(time.time() * 1000)
            elif(False == self.getConnectStatus()):
                self.startFlag = False

            time.sleep(self.interval_)

        self.logger.info("rttsend END")

    def processing(self):
        self.tcpsock.setReceiveProcess(self.tcpReceiveProcess)
        th1 = threading.Thread(target=self.tcpsock.receive)
        th1.start()
        th2 = threading.Thread(target=self.rttsend)
        th2.start()
        seqno = 0

        while(not self.stopFlag):
            ret,encimg = self.framep.getCode()

            if(self.startFlag == False or ret == False):
                self.logger.debug("sleep : have not getCode")
                time.sleep(1/30)
                continue

            if(self.outputflag == 1):
                    if(not os.path.exists("./datalog")):
                        os.mkdir("./datalog")
                    self.logger.debug("self.outputflag -> True")
                    output = "datalog/" + str(int(time.time() * 1000)) + ".jpg"
                    ff = open(output, 'wb') 
                    ff.write(encimg.tobytes())
                    ff.close()
            imagedata = json.dumps({"IMAGE":{"seqno":seqno,"len":encimg.size}})
            self.logger.info(imagedata)

            self.udpsock.send(imagedata.encode())

            if encimg.size > 4096:
                length = int(encimg.size/4096)

                cnt = 0
                for i in range(length):
                    senddata = encimg[cnt:i*4096+4096]
                    self.udpsock.send(senddata.tobytes())
                    cnt += 4096
                    msg = "count : "+ str(i)
                    self.logger.info(msg)

                    msg = "send imagedata : "+ str(senddata.tobytes())
                    self.logger.info(msg)
                    time.sleep(1/300)
                
                msg = "count : "+ str(length)
                self.logger.info(msg)

                msg = "send imagedata : "+ str(senddata.tobytes())
                self.logger.info(msg)

                self.udpsock.send(encimg[cnt:(cnt+int(encimg.size%4096))].tobytes())
            else:
                self.udpsock.send(encimg.tobytes())

            seqno = seqno+1
            time.sleep(1/30)

        th2.join()
        self.tcpsock.stop()
        th1.join()

        self.logger.info("receiver END")