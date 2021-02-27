import json, pprint
import config, keys, sys, logging
from datetime import datetime
from binance.client import Client
from binance.enums import *
from binance.websockets import BinanceSocketManager

#SOCKET = "wss://stream.binance.com:9443/ws/thetausdt@kline_1m"

candlefile = None

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')



# https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#klinecandlestick-streams
#
# Payload:
# 
# {
#   "e": "kline",     // Event type
#   "E": 123456789,   // Event time
#   "s": "BNBBTC",    // Symbol
#   "k": {
#     "t": 123400000, // Kline start time
#     "T": 123460000, // Kline close time
#     "s": "BNBBTC",  // Symbol
#     "i": "1m",      // Interval
#     "f": 100,       // First trade ID
#     "L": 200,       // Last trade ID
#     "o": "0.0010",  // Open price
#     "c": "0.0020",  // Close price
#     "h": "0.0025",  // High price
#     "l": "0.0015",  // Low price
#     "v": "1000",    // Base asset volume
#     "n": 100,       // Number of trades
#     "x": false,     // Is this kline closed?
#     "q": "1.0000",  // Quote asset volume
#     "V": "500",     // Taker buy base asset volume
#     "Q": "0.500",   // Taker buy quote asset volume
##    "B": "123456"   // Ignore
#   }
# }


# Taker buy means the buyer is the taker and seller is the maker.
# 
# Base asset means the quantity is expressed as the amount of coins that
# were received by the buyer (as opposed to quote asset which would be the
# amount paid by the buyer in btc/eth/usdt, depending on the market)
# 
# 'Volume' is the total amount of traded coins in the timeframe, disregarding which side is the taker
# 
# So basically to calculate maker buy volume (or taker sell, which is the same):
# 
# 'Volume' - ' Taker buy base asset volume' = ' Maker buy base asset volume'

def on_message(msg):

    global candlefile

    #print("message type: {}".format(msg['e']))
    #pprint.pprint(msg)

    # do something
    if msg['e'] == 'kline':

        #print('received message')
        print('*', end='')
        sys.stdout.flush()

        kline = msg['k']

        is_candle_closed = kline['x']
        close            = kline['c']
        
        candle = {}
        for elem in {'c', 'T', 'o', 'h', 'l', 'V' }:
            candle[elem] = kline[elem]  

        if is_candle_closed:
            print("candle closed at {}".format(close))
            #print(close, file=open('ticks.txt', 'a'))
            #logging.info(str(datetime.now()) + " , " + close)
            candlefile.write(json.dumps(candle) + "\n")
            candlefile.flush()

    elif msg['e'] == 'error':
        print ("Error message received!")
        logging.debug(msg)

if __name__ == '__main__':

    candlefile = open("candles1m.txt",'a')
    # perform file operations

    logging.basicConfig(filename='logfile.txt', level=logging.DEBUG)

    client   = Client(keys.API_KEY, keys.API_SECRET)
    bm       = BinanceSocketManager(client)
    print (bm )

    #conn_key = bm.start_kline_socket(config.TRADE_SYMBOL, on_message)
    #conn_key = bm.start_symbol_ticker_socket(config.TRADE_SYMBOL, on_message)
    conn_key = bm.start_kline_socket(config.TRADE_SYMBOL, on_message, interval=KLINE_INTERVAL_1MINUTE)
    #conn_key = bm.start_kline_socket(config.TRADE_SYMBOL, on_message)
    #conn_key = bm.start_kline_socket('THETAUSDT', process_message)
    print (conn_key )

    bm.start()
                
    #ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
    #ws.run_forever()

