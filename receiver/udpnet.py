from asyncio.windows_events import NULL
from logging import exception
import socket

class udpnet():
    def __init__(self,srcipaddr,dstipaddr,sendportNum,recvportNum):
        self.s_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.srcipaddr_ = srcipaddr
        self.dstipaddr_ = dstipaddr
        self.sendportNum_ = sendportNum
        self.recvportNum_ = recvportNum
        self.stopFlag = False
        self.processmethod_ = NULL

    def send(self,senddata):
        self.s_.sendto(senddata,(self.dstipaddr_,int(self.sendportNum_)))

    def receive(self):

        while(not self.stopFlag):

            if(not self.s_):
                self.s_.open()
            
            self.s_.bind((self.srcipaddr_,int(self.recvportNum_)))

            while(1):
                try:
                    recvdata = self.s_.recvfrom(1024)
                    msg = "senddata:" + str(recvdata)
                    self.processmethod_(recvdata)
                except:
                    self.s_.close()
                    break

    def reset(self):
        self.s_.close()

    def setReceiveProcess(self,processmethod):
        self.processmethod_ = processmethod

    def stop(self):
        self.stopFlag = True