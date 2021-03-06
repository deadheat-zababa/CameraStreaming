# coding: utf-8
import queue
import time
import struct
import json
import sys
sys.path.append("../common")
from tcpnet import tcpnet
from udpnet import udpnet
import threading

class sender():
    def __init__(self,conf,fprocess,logger):
        self.connnectStatus = False
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

        
    def tcpReceiveProcess(self,recvdata):
        try:
            jdict = json.loads(recvdata)
            self.logger.info(jdict)
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
            raise Exception

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

        self.framep.updateQuqlity(self.quality)

    def rttsend(self):
        seqno = 0
        while(not self.stopFlag):
            if(True == self.startFlag):
                rttdata = json.dumps({"RTT_CAL":{"seqno":seqno}})
                msg = "[RTT]senddata:" + str(rttdata)
                self.logger.info(msg)
                self.tcpsock.send(rttdata.encode())
                seqno = seqno +1
                if(seqno > 999):
                    seqno = 0
                self.sendtime = int(time.time() * 1000)

            time.sleep(self.interval_)

    def processing(self):
        #logging.info("sender START")
        self.tcpsock.setReceiveProcess(self.tcpReceiveProcess)
        th1 = threading.Thread(target=self.tcpsock.receive)
        th1.start()
        th2 = threading.Thread(target=self.rttsend)
        th2.start()
        seqno = 0

        while(not self.stopFlag):
            ret,encimg = self.framep.getCode()

            if(self.startFlag == False or ret == False):
                time.sleep(1/30)
                continue
            
            imagedata = json.dumps({"IMAGE":{"seqno":seqno,"len":encimg.size}})
            self.logger.info(imagedata)

            self.udpsock.send(imagedata.encode())

            if encimg.size > 1024:
                length = int(encimg.size/1024)
                #print(length)
                cnt = 0
                for i in range(length):
                    senddata = encimg[cnt:i*1024+1024]
                    self.udpsock.send(senddata.tobytes())
                    cnt += 1024
                    msg = "count : "+ str(i)
                    self.logger.info(msg)

                    msg = "send imagedata : "+ str(senddata)
                    self.logger.info(msg)
                    #tmp_img = encimg[cnt:i*1024+1024].tobytes()
                    #print(type(tmp_img))
                
                msg = "count : "+ str(length)
                self.logger.info(msg)

                msg = "send imagedata : "+ str(senddata)
                self.logger.info(msg)

                self.udpsock.send(encimg[cnt:(cnt+int(encimg.size%1024))].tobytes())
                #print(encimg[cnt:(cnt+int(encimg.size%1024))])
                #print((i+int(encimg.size%1024)))
            else:
                self.udpsock.send(encimg.tobytes())

            seqno = seqno+1
            time.sleep(1/120)

        th2.join()
        self.tcpsock.stop()
        th1.join()

        
        self.logger.info("receiver END")