import logging

class myLogDefine:
    TRACE = 0
    DEBUG = 1
    INFO = 2
    ERROR = 3
    CRITICAL = 4

class myLog:
    def __init__(self,logfilename='mylog.log'):
        self.logger = logging.getLogger('senderlog')
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.fh = logging.FileHandler(filename=logfilename)
        self.setLogLevel(2)
        self.fh.setFormatter(self.formatter)
        self.logger.addHandler(self.fh)

    def setLogLevel(self,level):
        #0 -> trace
        #1 -> debug
        #2 -> info
        #3 -> error
        #4 -> critical
        #if(myLogDefine.TRACE == level):
        #    self.fh.setLevel(myLogDefine.TRACE)
        if(myLogDefine.DEBUG == level):
            self.logger.setLevel(logging.DEBUG)
            self.fh.setLevel(logging.DEBUG)
        elif(myLogDefine.INFO == level):
            self.logger.setLevel(logging.INFO)
            self.fh.setLevel(logging.INFO)
        elif(myLogDefine.ERROR == level):
            self.logger.setLevel(logging.ERROR)
            self.fh.setLevel(logging.ERROR)
        elif(myLogDefine.CRITICAL == level):
            self.logger.setLevel(logging.CRITICAL)
            self.fh.setLevel(logging.CRITICAL)


    #def trace(self,msg):
    #    self.logger.trace(msg)

    def debug(self,msg):
        self.logger.debug(msg)

    def info(self,msg):
        self.logger.info(msg)

    def error(self,msg):
        self.logger.error(msg)

    def critical(self,msg):
        self.logger.critical(msg)


    

    

