
from logging.handlers import TimedRotatingFileHandler
class  SafeTimedRotatingFileHandler (TimedRotatingFileHandler):
    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename + "." +
                                     time.strftime(self.suffix, timeTuple))

        #if not os.path.exists(dfn) and os.path.exists(self.baseFilename):#changed 方式一
        #    os.rename(self.baseFilename,dfn)#change

        if not os.path.exists(dfn): #方式二
            f = open(self.baseFilename, 'a')
            fcntl.lockf(f.fileno(), fcntl.LOCK_EX)
            if not os.path.exists(dfn):
                os.rename(self.baseFilename, dfn)
            # 释放锁 释放老 log 句柄
            f.close()

        #self.rotate(self.baseFilename, dfn)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        #If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt
        
        
        
#日志初始化
def initlog(programe, str):

    path = os.path.realpath(str)
    if os.path.isdir(path):
        valid_path = os.path.abspath(path)
    else:
        print('path:{path} is not dir'.format(path = path))
        return False

    log_path = os.path.join(valid_path,programe)

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    #added by yll
    if not os.path.isdir(log_path):
        print('initlog',log_path,' exists but not dir!!!')
        return False


    FILENAME=programe
    LOG_FILE = os.path.join(log_path, FILENAME)
    #LOGGING_MSG_FORMAT  = '[%(asctime)s][%(thread)d] [%(levelname)s]  %(message)s'
    LOGGING_MSG_FORMAT  = '[%(asctime)s][%(levelname)s][%(funcName)s:%(lineno)d]  %(message)s'
    LOGGING_DATE_FORMAT = '%Y-%m-%d-%H:%M:%S'

    logger=logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter=logging.Formatter(LOGGING_MSG_FORMAT)
    
    #midnight

    hdlr=logging.handlers.SafeTimedRotatingFileHandler(LOG_FILE,when='midnight',interval=1,backupCount=0)
    hdlr.suffix='%Y%m%d.log'

    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    return logger
