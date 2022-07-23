import logging

class myLogDefine:
    TRACE = 0
    DEBUG = 1
    INFO = 2
    ERROR = 3
    CRITICAL = 4

class myLog:
    def __init__(self,logfilename='mylog'):
        self.logger = logging.getLogger(logfilename)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.fh = logging.FileHandler(filename='log.txt')
        self.fh.setLevel(logging.INFO)
        self.fh.setFormatter(logging.formatter)
        self.logger.addHandler(logging.fh)

    def setLogLevel(self,level):
        #0 -> trace
        #1 -> debug
        #2 -> info
        #3 -> error
        #4 -> critical
        #if(myLogDefine.TRACE == level):
        #    self.fh.setLevel(myLogDefine.TRACE)
        if(myLogDefine.DEBUG == level):
            self.fh.setLevel(myLogDefine.DEBUG)
        elif(myLogDefine.INFO == level):
            self.fh.setLevel(myLogDefine.INFO)
        elif(myLogDefine.ERROR == level):
            self.fh.setLevel(myLogDefine.ERROR)
        elif(myLogDefine.CRITICAL == level):
            self.fh.setLevel(myLogDefine.CRITICAL)


    def trace(self,msg):
        self.logger.trace(msg)

    def debug(self,msg):
        self.logger.debug(msg)

    def info(self,msg):
        self.logger.info(msg)

    def error(self,msg):
        self.logger.error(msg)

    def critical(self,msg):
        self.logger.critical(msg)


    

    

