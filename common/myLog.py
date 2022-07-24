import logging

class myLogDefine:
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    CRITICAL = 5

class myLog:
    def __init__(self,logfilename='mylog.log'):
        self.logger = logging.getLogger('senderlog')
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.fh = logging.FileHandler(filename=logfilename)
        self.setLogLevel(2)
        self.fh.setFormatter(self.formatter)
        self.logger.addHandler(self.fh)

    def setLogLevel(self,level):
        #1 -> debug
        #2 -> info
        #3 -> warn
        #4 -> error
        #5 -> critical
        if(myLogDefine.DEBUG == level):
            self.logger.setLevel(logging.DEBUG)
            self.fh.setLevel(logging.DEBUG)
        
        elif(myLogDefine.INFO == level):
            self.logger.setLevel(logging.INFO)
            self.fh.setLevel(logging.INFO)

        elif(myLogDefine.WARN == level):
            self.logger.setLevel(logging.WARN)
            self.fh.setLevel(logging.WARN)
        
        elif(myLogDefine.ERROR == level):
            self.logger.setLevel(logging.ERROR)
            self.fh.setLevel(logging.ERROR)
        
        elif(myLogDefine.CRITICAL == level):
            self.logger.setLevel(logging.CRITICAL)
            self.fh.setLevel(logging.CRITICAL)


    

    def debug(self,msg):
        self.logger.debug(msg)

    def info(self,msg):
        self.logger.info(msg)

    def warn(self,msg):
        self.logger.warn(msg)

    def error(self,msg):
        self.logger.error(msg)

    def critical(self,msg):
        self.logger.critical(msg)


    

    

