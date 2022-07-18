from logging import exception
import socket

class tcpnet():
    def __init__(self,ipaddr,portNum):
        self.s_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ipaddr_ = ipaddr
        self.portNum_ = portNum
        self.stopFlag = False

    def connect(self):
        if(not self.s_):
            self.s_.open()

        self.s_.timeout(1)
        while(1):
            try:
                self.s_.connect((self.ipaddr_,int(self.portNum_)))
                break
            except:
                print('err')

    def accept(self):
        
        if(not self.s_):
            self.s_.open()

        self.s_.bind((self.ipaddr_,int(self.portNum)))
        self.s_.listen(4)
        self.s_,address = self.s_.accept()

    def send(self,senddata):
        self.s_.send(senddata)

    def receive(self):

        while(not self.stopFlag):
            
            self.accept()

            while(1):
                try:
                    self.s_.recv(1024)
                    self.processmethod_()
                except:
                    self.s_.close()
                    break

    def reset(self):
        self.s_.close()

    def setReceiveProcess(self,processmethod):
        self.processmethod_ = processmethod

    def stop(self):
        self.stopFlag = True