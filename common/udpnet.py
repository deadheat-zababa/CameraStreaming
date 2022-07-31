from asyncio.windows_events import NULL
import socket

class udpnet():
    def __init__(self,srcipaddr,dstipaddr,sendportNum,recvportNum,logger):
        self.s_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.srcipaddr_ = srcipaddr.strip('""')
        self.dstipaddr_ = dstipaddr.strip('""')
        self.sendportNum_ = sendportNum
        self.recvportNum_ = recvportNum
        self.stopFlag = False
        self.processmethod_ = NULL
        self.logger = logger

        msg = "IP ADDR(SRC):" + str(self.srcipaddr_) + "\n" + "PORT NUMBER(RECV):"  + str(self.recvportNum_) + "\n"+ "IP ADDR(DST):" + str(self.dstipaddr_) + "\n" + "PORT NUMBER(SEND):" + str(self.sendportNum_)
        self.logger.info(msg)

        self.s_.bind((self.srcipaddr_,int(self.recvportNum_)))

    def send(self,senddata):
        self.s_.sendto(senddata,(self.dstipaddr_,int(self.sendportNum_)))

    def receive(self):

        while(not self.stopFlag):

            if(not self.s_):
                self.s_.open()
                
            while(1):
                try:
                    recvdata = self.s_.recvfrom(1024)
                    msg = "recvdata:" + str(recvdata[0])
                    self.logger.debug(msg)
                    self.processmethod_(recvdata[0])
                except:
                    self.logger.error("udp receie: error")
                    if(self.s_):
                        self.s_.close()
                    break

        self.logger.info("udp receie end")

    def setReceiveProcess(self,processmethod):
        self.processmethod_ = processmethod

    def stop(self):
        self.s_.close()
        self.stopFlag = True