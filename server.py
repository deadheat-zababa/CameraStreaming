# coding: utf-8
import cv2
import numpy as np
import logging
import threading
import queue
import time
import socket
import struct

logging.basicConfig(filename='test.log',level=logging.DEBUG)
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),5]
quality = 50


class controlThread(threading.Thread):
    def __init__(self,ipAddr,portNum):
        threading.Thread.__init__(self)
        self.ipAddr = ipAddr
        self.portNum = portNum
        self.timestamp = 0
        self.stop_event =threading.Event()
        self.setDaemon(True)

    def stop(self):
        self.stop_event.set()

    def run(self):

        seqno = 0
        
        clientsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        clientsocket.bind((socket.gethostname(),self.portNum))
        clientsocket.listen(5)

        clientsocket,address = clientsocket.accept()

        while(True):
            recvData = clientsocket.recv(1024)

            t = timestampo()
            dictData = json.load(recvData)

            if '' in dictData:

            else if '' in dictData:

            else:
                print("error : exception data")

            #スループット計算
            

            print("while end")
        
        clientsocket.close()


#--------------------------------------------------------
class socketThread(threading.Thread):
    def __init__(self,ipAddr,portNum,timestamp,q):
        threading.Thread.__init__(self)
        self.ipAddr = ipAddr
        self.portNum = portNum
        self.timestamp = timestamp
        self.q = q
        self.stop_event =threading.Event()
        self.setDaemon(True)

    def stop(self):
        self.stop_event.set()

    def getFrame(self):
        #if self.q.qsize() == 0:
        #    return False
        
        #print("enc buf:",buf.shape)
        #print("enc buf:",type(buf))
        #print("enc buf:",buf.size)
        #else:
            #self.q.get()
            #cv2.imshow(str(self.portNum),buf)
        print("getFrame")
        return True, self.q.get()

    def run(self):

        clientsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        clientsocket.bind((socket.gethostname(),self.portNum))
        clientsocket.listen(5)
        logging.info("socket Thread Start")

        clientsocket,address = clientsocket.accept()
        clientsocket.send(struct.pack('>L',self.timestamp))
        
        #clientsocket.close()
        logging.info("send timestamp")
        quality = 5
        
        while(True):
            print("while loop")
            ret,img = self.getFrame()
            
            if(ret):
                #get frame data
                print("img encode")
                ret, encimg = cv2.imencode(".jpg",img,[int(cv2.IMWRITE_JPEG_QUALITY),quality])
                if False == ret:
                    logging.error("Encode error")
                    continue

                else:
                    logging.info("Encode OK:%s",encimg.shape)
                    #print(type(encimg))
                    #print(encimg.size)

            else:
                logging.info("empty Queue")
                continue

            quality += 1
            if quality>90:
                quality = 90

            
            #print(encimg)
            clientsocket.send(struct.pack('>L',encimg.size))
            #print(type(encimg)) 
            #print(encimg.shape)

            if encimg.size > 1024:
                encimg.ravel
                length = int(encimg.size/1024)
                #print(length)
                cnt = 0
                for i in range(length):
                    clientsocket.send(encimg[cnt:i*1024+1024].tobytes())
                    cnt += 1024
                    tmp_img = encimg[cnt:i*1024+1024].tobytes()
                    #print(type(tmp_img))

                clientsocket.send(encimg[cnt:(cnt+int(encimg.size%1024))].tobytes())
                #print(encimg[cnt:(cnt+int(encimg.size%1024))])
                #print((i+int(encimg.size%1024)))
            else:
                clientsocket.send(encimg.tobytes())
                
            logging.info("send data")
            
            #img1 = cv2.imdecode(encimg,cv2.IMREAD_UNCHANGED)
            #cv2.imshow('window name2',img1)
            
            #print("sleep")
            cv2.waitKey(1)
            time.sleep(1/30)

        cv2.destroyAllWindows()
            
        print("while end")
        clientsocket.close()

#------------------------------------------------------------
def main():
    logging.info("START")

    #read a dll
    #dll = cdll.loadLibrary(".dll")

    q1 = queue.Queue()
    #q2 = queue.Queue()
    #q3 = queue.Queue()
    #q4 = queue.Queue()

    #get timestamp
    st = int(time.time())+5

    t1 = socketThread("127.0.0.1",12345,st,q1)
    #t2 = socketThread("127.0.0.1",12346,st,q2)
    #t3 = socketThread("127.0.0.1",12347,st,q3)
    #t4 = socketThread("127.0.0.1",12348,st,q4)

    t1.start()
    #t2.start()
    #t3.start()
    #t4.start()
    capture = cv2.VideoCapture(0)

    firstflag = False

    while(True):
        ret,frame = capture.read()
        #cv2.imshow('window name',frame)
        #cv2.moveWindow('window name', 300, 200)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            logging.info("end")
            break

        else:
            #if (q1.empty()): #& q2.empty() & q3.empty() & q4.empty())):
            logging.debug("frame:%d,%s",frame.size,frame.shape)
                #frameはndarrayなのでnumpyで処理
            tmp_img1 = frame[0:int(frame.shape[0]/2), 0:int(frame.shape[1])]
                #tmp_img2 = frame[int(frame.shape[0]/2):int(frame.shape[0]), 0:int(frame.shape[1])]

                #-------------
                #--q1--|--q2--
                #------|------
                #--q3--|--q4--
                #------|------
            tmp = tmp_img1[0:tmp_img1.shape[0],0:int(tmp_img1.shape[1]/2)]
            q1.put(tmp)
            print("get cam")
                #print(tmp)
                #q2.put(tmp_img1[0:tmp_img1.shape[0],int(tmp_img1.shape[1]/2):tmp_img1.shape[1]])
                #q3.put(tmp_img2[0:tmp_img2.shape[0],0:int(tmp_img2.shape[1]/2)])
                #q4.put(tmp_img2[0:tmp_img2.shape[0],int(tmp_img2.shape[1]/2):tmp_img2.shape[1]])

                #img2 = tmp_img1[0:tmp_img1.shape[0],0:int(tmp_img1.shape[1]/2)]
                #print(type(frame))
                #img2 = q1.get()
                #print("img2:",img2.shape)
                #print("img2:", type(img2))
                #print("img2:",img2.size)
                #cv2.imshow('window name3',img2)
                #cv2.moveWindow('window name3', 0, 480)
                #cv2.imshow('window name4',tmp_img1[0:tmp_img1.shape[0],int(tmp_img1.shape[1]/2):tmp_img1.shape[1]])
                #cv2.moveWindow('window name4', 640, 480)
                #cv2.imshow('window name1',tmp_img2[0:tmp_img2.shape[0],0:int(tmp_img2.shape[1]/2)])
                #cv2.moveWindow('window name1', 0, 0)
                #cv2.imshow('window name2',tmp_img2[0:tmp_img2.shape[0],int(tmp_img2.shape[1]/2):tmp_img2.shape[1]])
                #cv2.moveWindow('window name2',640, 0)

            #else:
            #    print("Empty")
            #    logging.info("Empty")
            
        logging.debug("Sleep:%f",1/capture.get(3))
        time.sleep(1/capture.get(3))
        firstflag = True

    t1.stop()
    #t2.stop()
    #t3.stop()
    #t4.stop()
    #t1.join()
    #t2.join()
    #t3.join()
    #t4.join()
    capture.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
