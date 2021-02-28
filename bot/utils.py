import time

def timestamp2str( ts ):
    if ts == None: 
        return None

    if type(ts) is not int:
        raise Exception('invalid datetime: input should be an int; input: %s' % (ts ))

    date_time = time.gmtime(ts/1000)
    return time.strftime("%m/%d/%Y, %H:%M:%S",date_time)


