import time, logging, pprint
from datetime import datetime

logging.basicConfig(filename='logfile.txt', level=logging.DEBUG)

def timestamp2str(ts):
    if ts == None: 
        return None

    if type(ts) is not int:
        raise Exception('invalid datetime: input should be an int; input: %s' % (ts ))

    date_time = time.gmtime(ts/1000)
    return time.strftime("%m/%d/%Y, %H:%M:%S",date_time)

def calc_average(num):
    sum_num = 0
    for t in num:
        sum_num = sum_num + t

    avg = sum_num / len(num)
    return avg

def dprint(msg):
    logging.info(str(datetime.now()) + ": " + msg)

def dpprint(obj):
    str = pprint.pformat(obj)
    dprint(str)
