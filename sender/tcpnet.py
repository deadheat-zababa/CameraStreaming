from logging import exception
import socket
import time


class tcpnet():
    def __init__(self,ipaddr,portNum,mode,logger):
        self.s_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ipaddr_ = ipaddr.strip('""')
        self.portNum_ = int(portNum)
        self.stopFlag = False
        self.connectStatus = False
        self.logger = logger
        self.mode = mode
        
    def getConnectStatus(self):
        return self.connectStatus

    def connect(self):
    
        while(not self.stopFlag):
            try:
                if(not self.s_):
                    self.s_.open()

                server = (self.ipaddr_,self.portNum_)
                self.s_.connect(server)
                self.connectStatus = True
                self.logger.info("conncet succcess")
                break
            except Exception as e:
                self.logger.error(e)
                time.sleep(1)
        self.logger.debug("connect end")

    def accept(self):
        
        if(not self.s_):
            self.s_.open()

        self.s_.bind((self.ipaddr_,self.portNum))
        self.s_.listen(4)
        self.s_,address = self.s_.accept()

    def send(self,senddata):
        self.s_.send(senddata)

    def receive(self):

        while(not self.stopFlag):
            if(0 == self.mode):
                self.connect()

            if(self.stopFlag == True):
                break
            
            while(1):
                try:
                    recvdata = self.s_.recv(1024)
                    msg = "senddata:" + str(recvdata)
                    self.logger.info(msg)
                    self.processmethod_(recvdata)
                except:
                    self.logger.info("close sock")
                    self.s_.close()
                    self.connectStatus = False
                    break

    def reset(self):
        self.s_.close()

    def setReceiveProcess(self,processmethod):
        self.processmethod_ = processmethod

    def stop(self):
        self.logger.info("stop")
        self.stopFlag = True