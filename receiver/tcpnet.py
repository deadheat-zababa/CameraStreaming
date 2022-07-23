from logging import exception
import socket

class tcpnet():
    def __init__(self,ipaddr,portNum):
        self.s_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ipaddr_ = ipaddr.strip('""')
        self.portNum_ = portNum
        self.stopFlag = False
        self.connctStatus = False

    def getConnectStatus(self):
        return self.connctStatus


    def connect(self):
        if(not self.s_):
            self.s_.open()

        while(1):
            try:
                server = (self.ipaddr_,self.portNum_)
                self.s_.connect((self.ipaddr_,int(self.portNum_)))
                break
            except:
                print('err')

    def accept(self):
        print("listen")
        if(not self.s_):
            self.s_.open()

        server = (self.ipaddr_,self.portNum_)
        self.s_.bind(server)
        self.s_.listen()
        self.s_,address = self.s_.accept()

    def send(self,senddata):
        self.s_.send(senddata)

    def receive(self):

        while(not self.stopFlag):
            
            self.accept()

            self.connctStatus = True

            while(1):
                try:
                    recvdata = self.s_.recv(1024)
                    msg = "senddata:" + str(recvdata)
                    self.processmethod_(recvdata)
                except:
                    self.s_.close()
                    self.connctStatus = False
                    break

    def reset(self):
        self.s_.close()

    def setReceiveProcess(self,processmethod):
        self.processmethod_ = processmethod

    def stop(self):
        self.stopFlag = True