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
        msg = "IP ADDR:" + str(self.ipaddr_) + "\n" + "PORT NUMBER:" + str(self.portNum_)
        self.logger.info(msg)
        
    def getConnectStatus(self):
        return self.connectStatus

    def connect(self):
    
        while(not self.stopFlag):
            try:
                if(not self.s_):
                    self.s_.open()

                server = (self.ipaddr_,self.portNum_)
                self.s_.settimeout(1000)
                self.s_.connect(server)
                self.connectStatus = True
                self.s_.settimeout(None)
                self.logger.info("conncet succcess")
                break
            except Exception as e:
                self.logger.error(e)
                time.sleep(1)
        self.logger.debug("connect end")

    def accept(self):
        try:
            self.logger.info("listen")
            if(not self.s_):
                self.s_.open()

            server = (self.ipaddr_,self.portNum_)
            self.s_.bind(server)
            self.s_.listen()
            self.s_,address = self.s_.accept()
        except:
            self.logger.error("Error:accept")

    def send(self,senddata):
        try:
            self.s_.send(senddata)
        except:
            self.logger.error("send error")
            self.reset()

    def receive(self):

        while(not self.stopFlag):

            if(0 == self.mode):
                self.connect()
            
            elif(1 == self.mode):
                self.accept()
                self.connectStatus = True
                self.logger.info("accept success")

            if(self.stopFlag == True):
                break
            
            while(1):
                try:
                    recvdata = self.s_.recv(1024)

                    msg = "recvdata:" + str(recvdata)
                    self.logger.info(msg)
                    self.processmethod_(recvdata)
                except:
                    self.logger.info("close sock")
                    self.s_.close()
                    self.connectStatus = False
                    time.sleep(1)
                    break

    def reset(self):
         if(self.s_):
                self.s_.close()

    def setReceiveProcess(self,processmethod):
        self.processmethod_ = processmethod

    def stop(self):
        self.logger.info("stop")
        self.reset()
        self.stopFlag = True