import socket
from itertools import count
import time

class udpnet():
    def __init__(self,srcipaddr,dstipaddr,sendportNum,recvportNum,logger):
        self.s_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.srcipaddr_ = srcipaddr.strip('""')
        self.dstipaddr_ = dstipaddr.strip('""')
        self.sendportNum_ = sendportNum
        self.recvportNum_ = recvportNum
        self.stopFlag = False
        self.processmethod_ = None
        self.logger = logger
        bufsize = self.s_.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) 
        self.s_.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,bufsize*100)
        #bufsize = self.s_.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        #print(str(bufsize))
        msg = "IP ADDR(SRC):" + str(self.srcipaddr_) + "\n" + "PORT NUMBER(RECV):"  + str(self.recvportNum_) + "\n"+ "IP ADDR(DST):" + str(self.dstipaddr_) + "\n" + "PORT NUMBER(SEND):" + str(self.sendportNum_)
        self.logger.info(msg)

        self.s_.bind((self.srcipaddr_,int(self.recvportNum_)))

    def send(self,senddata):
        try:
            self.logger.debug(str(senddata))
            self.s_.sendto(senddata,(self.dstipaddr_,int(self.sendportNum_)))
        except:
            self.logger.error("udp send error")
            self.s_.close()
            self.s_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def receive(self):

        for i in count():
            if(self.stopFlag == True):
                break
            for j in count():
                try: 
                    time_sta = time.time()
                    recvdata = self.s_.recvfrom(4096)

                    self.processmethod_(recvdata[0])
                    time_end = time.time()

                    diff_time = time_end- time_sta

                    self.logger.info("getprocessing time : "+str(diff_time))

                except:
                    self.logger.error("udp receie: error")
                    self.s_.close()
                    self.s_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    self.s_.bind((self.srcipaddr_,int(self.recvportNum_)))
                    break

        self.s_.close()
        self.logger.info("udp receie end")

    def setReceiveProcess(self,processmethod):
        self.processmethod_ = processmethod

    def stop(self):
        self.s_.close()
        self.stopFlag = True