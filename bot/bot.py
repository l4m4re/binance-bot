import json, pprint, talib, numpy
import config
import sys, time, os
from trader import *
from broker import *

#TRADE_SYMBOL    = "THETAUSDT"
TRADE_SYMBOL    = "BTCUSDT"
#TICKER_FILE     = "../data/BTCUSDT_2020_1minutes.txt"
TICKER_FILE     = "../data/BTCUSDT_2021_1minutes.txt"
TRADE_QUANTITY  = 10

trader = None
broker = None
    
def follow(thefile):
    '''generator function that yields new lines in a file
    '''

    # seek the end of the file
    #thefile.seek(0, os.SEEK_END)
    
    # start infinite loop
    while True:
        # read last line of file
        line = thefile.readline()        # sleep if file hasn't been updated
        if not line:
            time.sleep(0.1)
            broker.goLive(True)
            continue

        yield line

if __name__ == '__main__':

    #prices = client.get_all_tickers()
    #print(prices)

    #for price in prices:
    #    pprint.pprint(price)

    #info = client.get_exchange_info()
    #pprint.pprint( info )

    #info = client.get_symbol_info(TRADE_SYMBOL)
    #print( info )

    #klines = client.get_historical_klines(TRADE_SYMBOL, Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")
    #for kline in klines:
    #    print( kline )
  
    broker = Broker()
    trader = Trader(broker)
    
    datafile = open(TICKER_FILE,"r")
    datalines = follow(datafile)    # iterate over the generator
    for line in datalines:

        candle = {}
        inpcandle = json.loads(line)

        candle['T'] = int(inpcandle['T'])
        for elem in {'c', 'o', 'h', 'l', 'v' }:
            candle[elem] = float(inpcandle[elem])

        #pprint.pprint(candle)

        trader.append( candle )
                
